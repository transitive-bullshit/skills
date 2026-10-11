#!/usr/bin/env python3
"""Record local patches or verify pinned upstream snapshots reproduce effective skills."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tree_digest(root):
    """Hash paths, Git file modes and bytes, including symlink targets."""
    result = hashlib.sha256()
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            mode, content = '120000', os.readlink(path).encode()
        elif path.is_file():
            mode = '100755' if path.stat().st_mode & 0o111 else '100644'
            content = path.read_bytes()
        else:
            continue
        result.update(path.relative_to(root).as_posix().encode() + b'\0')
        result.update(mode.encode() + b'\0' + str(len(content)).encode() + b'\0' + content)
    return result.hexdigest()


def inside(repo, relative):
    path = (repo / relative).resolve()
    if not path.is_relative_to(repo.resolve()) or path == repo.resolve():
        raise ValueError(f'Path must be inside repository: {relative}')
    return path


def make_patch(pristine, effective):
    with tempfile.TemporaryDirectory(prefix='skill-patch-') as temporary:
        root = Path(temporary)
        shutil.copytree(pristine, root / 'a', symlinks=True)
        shutil.copytree(effective, root / 'b', symlinks=True)
        result = subprocess.run(['git', 'diff', '--no-index', '--binary', '--no-renames', '--no-ext-diff',
                                 '--no-textconv', '--no-prefix', '--', 'a', 'b'],
                                cwd=root, capture_output=True)
        if result.returncode not in (0, 1):
            raise ValueError(result.stderr.decode())
        return result.stdout


def replay(pristine, patch, expected):
    with tempfile.TemporaryDirectory(prefix='skill-replay-') as temporary:
        root = Path(temporary) / 'skill'
        shutil.copytree(pristine, root, symlinks=True)
        if patch:
            result = subprocess.run(['git', 'apply', '--binary', '--whitespace=nowarn', '-'],
                                    input=patch, cwd=root, capture_output=True)
            if result.returncode:
                raise ValueError('Patch does not apply: ' + result.stderr.decode())
        if tree_digest(root) != expected:
            raise ValueError('Snapshot plus patch does not reproduce effective skill')


def process_derived(repo, record, write=False, defer_write=False):
    """Verify frozen inputs; record only intentionally changed synthesized outputs."""
    skill = inside(repo, record['path'])
    lock_path = inside(skill, record['derivation']['lock'])
    lock = json.loads(lock_path.read_text())
    if lock.get('version') != 1 or not lock.get('sources') or not lock.get('outputs'):
        raise ValueError('Derived source lock requires version 1, sources and outputs')
    for source in lock['sources']:
        if not re.fullmatch(r'[0-9a-f]{40}', source.get('commit', '')):
            raise ValueError('Derived upstream source requires a full commit SHA')
        root = inside(skill, source['root'])
        listed = set()
        for item in source['files']:
            path = inside(root, item['path'])
            if path.is_symlink() or not path.is_file():
                raise ValueError(f'Source must be a regular file: {path}')
            content = path.read_bytes()
            mode = '100755' if path.stat().st_mode & 0o111 else '100644'
            blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
            if digest(content) != item['sha256'] or blob != item['gitBlob'] or mode != item['gitMode']:
                raise ValueError(f'Pinned source changed: {path}')
            listed.add(path.relative_to(root).as_posix())
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
        if listed != actual:
            raise ValueError(f'Unrecorded or missing source files: {root}')
    for item in lock['personalInputs']:
        if digest(inside(skill, item['path']).read_bytes()) != item['sha256']:
            raise ValueError(f'Personal input changed: {item["path"]}; version and review the input explicitly')
    for item in lock['outputs']:
        actual = digest(inside(skill, item['path']).read_bytes())
        if write:
            item['sha256'] = actual
        elif actual != item['sha256']:
            raise ValueError(f'Derived output changed: {item["path"]}; review and run upstream.py record')
    content = (json.dumps(lock, indent=2) + '\n').encode()
    if write and not defer_write:
        lock_path.write_bytes(content)
    return lock_path, content


def process(repo, record, write=False, defer_write=False):
    if 'derivation' in record:
        return process_derived(repo, record, write, defer_write)
    origin, tracking = record['origin'], record['upstream']
    if not re.fullmatch(r'[0-9a-f]{40}', origin.get('commit', '')):
        raise ValueError('Tracked upstream requires a full commit SHA')
    pristine = inside(repo, tracking['snapshot'])
    effective = inside(repo, record['path'])
    patch_path = inside(repo, tracking['patch'])
    if not (pristine / 'SKILL.md').is_file():
        raise ValueError('Missing pristine SKILL.md')
    snapshot_hash, effective_hash = tree_digest(pristine), tree_digest(effective)
    patch = make_patch(pristine, effective) if write else patch_path.read_bytes()
    replay(pristine, patch, effective_hash)
    hashes = {'snapshotSha256': snapshot_hash, 'patchSha256': digest(patch),
              'effectiveSha256': effective_hash}
    if write:
        if not defer_write:
            patch_path.parent.mkdir(parents=True, exist_ok=True)
            patch_path.write_bytes(patch)
        tracking.update(hashes)
    elif any(tracking.get(key) != value for key, value in hashes.items()):
        raise ValueError('Recorded hash differs; review changes and run upstream.py record')
    return patch_path, patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'record'])
    parser.add_argument('skills', nargs='*', help='Tracked skill names; defaults to all')
    args = parser.parse_args()
    manifest_path = REPO / 'skills.json'
    manifest = json.loads(manifest_path.read_text())
    if args.command == 'check' and not args.skills:
        missing = [name for name, row in manifest['skills'].items()
                   if row['origin']['kind'] == 'adopted' and 'upstream' not in row]
        if missing:
            parser.exit(1, 'Adopted skills without pinned snapshots: ' + ', '.join(missing) + '\n')
    names = args.skills or sorted(name for name, row in manifest['skills'].items()
                                 if 'upstream' in row or 'derivation' in row)
    errors, prepared = [], []
    for name in names:
        try:
            prepared.append(process(REPO, manifest['skills'][name], args.command == 'record', defer_write=True))
        except (ValueError, KeyError, OSError) as error:
            errors.append(f'{name}: {error}')
    if args.command == 'record' and not errors:
        for patch_path, patch in prepared:
            patch_path.parent.mkdir(parents=True, exist_ok=True)
            patch_path.write_bytes(patch)
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    derived = sum('derivation' in manifest['skills'][name] for name in names)
    suffix = f' and {derived} derived skill(s)' if derived else ''
    print(f'{"Recorded" if args.command == "record" else "Verified"} {len(names) - derived} upstream snapshots and local patches{suffix}')


if __name__ == '__main__':
    main()
