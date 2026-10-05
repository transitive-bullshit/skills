#!/usr/bin/env python3
"""Versioned skills and transactional user-level installation. Python 3.11+."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections import Counter
from datetime import datetime, timezone

API_VERSION = 1
REPO = Path(__file__).resolve().parents[1]
STATE = Path('.local/state/agent-env')
ENVIRONMENT_LINKS = {'.codex/AGENTS.md', '.claude/CLAUDE.md', '.local/bin/agent-env'}

if sys.version_info < (3, 11):
    sys.exit('skillset requires Python 3.11+')


class Conflict(Exception):
    pass


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.is_file() else default


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def fingerprint(path):
    if path.is_symlink():
        return {'link': os.readlink(path)}
    if not path.exists():
        return None
    if path.is_file():
        return {'file': hashlib.sha256(path.read_bytes()).hexdigest(), 'mode': path.stat().st_mode & 0o777}
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(path.rglob('*')):
            if child.is_symlink() or child.is_file():
                digest.update(str(child.relative_to(path)).encode() + b'\0')
                digest.update(json_bytes(fingerprint(child)))
        return {'directory': digest.hexdigest()}
    raise Conflict(f'Unsupported file type: {path}')


def safe_target(home, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts or str(relative) == '.':
        raise Conflict(f'Invalid installation path: {relative}')
    path = home / relative
    parent = path.parent
    while parent != home:
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise Conflict(f'Installation parent must be a directory: {parent}')
        parent = parent.parent
    return path


def load_catalog(repo=REPO):
    catalog = read_json(repo / 'skills.json')
    if not isinstance(catalog, dict) or catalog.get('version') != 1:
        raise Conflict('skills.json must use schema version 1')
    records, profiles = catalog.get('skills', {}), catalog.get('profiles', {})
    if not records or not profiles:
        raise Conflict('skills.json must define skills and profiles')
    names = set()
    for skill_id, record in records.items():
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', skill_id):
            raise Conflict(f'Invalid skill ID: {skill_id}')
        relative = Path(record['path'])
        directory = repo / relative
        if relative != Path('skills') / skill_id or directory.is_symlink():
            raise Conflict(f'{skill_id}: expected a real skills/{skill_id} directory')
        path = directory / 'SKILL.md'
        if not path.is_file():
            raise Conflict(f'Missing skill: {path}')
        source = path.read_text()
        front = source.split('---', 2)
        if not source.startswith('---\n') or len(front) < 3:
            raise Conflict(f'{skill_id}: missing frontmatter')
        match = re.search(r'^name:\s*(.+?)\s*$', front[1], re.M)
        name = match.group(1).strip('\"\'') if match else None
        if name != skill_id:
            raise Conflict(f'{skill_id}: frontmatter name must match its directory (found {name!r})')
        if name in names:
            raise Conflict(f'Duplicate skill name: {name}')
        names.add(name)
        if not re.search(r'^description:\s*\S', front[1], re.M):
            raise Conflict(f'{skill_id}: description is required')
        nested = [p for p in directory.rglob('SKILL.md') if p != path]
        if nested:
            raise Conflict(f'{skill_id}: nested skill root: {nested[0].relative_to(repo)}')
        for p in directory.rglob('*'):
            if p.is_symlink() and (not p.exists() or not p.resolve().is_relative_to(directory.resolve())):
                raise Conflict(f'{skill_id}: broken or external resource link: {p.relative_to(repo)}')
        origin = record.get('origin', {})
        if origin.get('kind') not in {'personal', 'adopted', 'local'}:
            raise Conflict(f'{skill_id}: missing provenance')
        if origin['kind'] == 'adopted' and not all(origin.get(k) for k in ['repository', 'path', 'baseline']):
            raise Conflict(f'{skill_id}: adopted skill requires repository, path, and baseline')
        license_info = origin.get('license', {})
        if license_info.get('file'):
            license_path = (repo / license_info['file']).resolve()
            if not license_path.is_relative_to(repo.resolve()) or not license_path.is_file():
                raise Conflict(f'{skill_id}: missing or external license file')
            if hashlib.sha256(license_path.read_bytes()).hexdigest() != license_info.get('sha256'):
                raise Conflict(f'{skill_id}: license content differs from its recorded hash')
        if not isinstance(record.get('requires', []), list):
            raise Conflict(f'{skill_id}: requires must be a list of command names')
    directories = {p.name for p in (repo / 'skills').iterdir() if p.is_dir()}
    if directories != set(records):
        raise Conflict(f'Unregistered or missing skill directories: {sorted(directories ^ set(records))}')
    for profile in profiles:
        select(catalog, profile)
    return catalog


def select(catalog, profile, trail=()):
    if profile in trail:
        raise Conflict(f'Profile cycle: {" -> ".join((*trail, profile))}')
    if profile not in catalog['profiles']:
        raise Conflict(f'Unknown skill profile: {profile}')
    entry = catalog['profiles'][profile]
    selected = set(entry.get('skills', []))
    unknown = selected - catalog['skills'].keys()
    if unknown:
        raise Conflict(f'{profile}: unknown skills: {sorted(unknown)}')
    for parent in entry.get('extends', []):
        selected.update(select(catalog, parent, (*trail, profile)))
    return sorted(selected)


def desired_links(repo, home, catalog, profile, agents):
    links = {}
    for skill_id in select(catalog, profile):
        shared = f'.agents/skills/{skill_id}'
        links[shared] = str(repo / catalog['skills'][skill_id]['path'])
        if 'claude' in agents:
            links[f'.claude/skills/{skill_id}'] = str(home / shared)
    return links


def owned_path(relative):
    path = Path(relative)
    return (len(path.parts) == 3 and path.parts[:2] in [('.agents', 'skills'), ('.claude', 'skills')]
            and bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', path.name))) or str(path) in ENVIRONMENT_LINKS


def link_plan(home, desired, previous, adopt=False):
    operations, errors = [], []
    for relative in set(previous) | set(desired):
        if not owned_path(relative):
            raise Conflict(f'Unrecognized managed link in state: {relative}')
    for relative in sorted(set(previous) | set(desired)):
        target = safe_target(home, relative)
        before = fingerprint(target)
        source = desired.get(relative)
        current_link = before.get('link') if isinstance(before, dict) else None
        owned = current_link is not None and current_link == previous.get(relative)
        if source is None:
            if before is not None and not owned:
                errors.append(f'Changed managed target: {target}; preserve or restore it before applying')
            elif owned:
                operations.append({'path': relative, 'before': before, 'kind': 'remove'})
        elif current_link is not None and (target.parent / current_link).resolve() == Path(source).resolve():
            continue
        elif before is None or owned or adopt:
            operations.append({'path': relative, 'before': before, 'kind': 'link', 'source': source})
        else:
            errors.append(f'Unmanaged target: {target}; use --adopt to back it up first')
    if errors:
        raise Conflict('\n'.join(errors))
    return operations


def write_plan(home, relative, content, mode=0o600, adopt=False):
    target = safe_target(home, relative)
    if target.is_symlink() and not adopt:
        raise Conflict(f'Refusing to replace a linked configuration/state file: {target}')
    if target.exists() and not target.is_file():
        raise Conflict(f'Expected a file: {target}')
    if target.is_file() and not target.is_symlink() and target.read_bytes() == content:
        return []
    return [{'path': str(relative), 'before': fingerprint(target), 'kind': 'write', 'content': content, 'mode': mode}]


def describe(operations):
    return [f'{op["kind"]}: {op["path"]}' + (f' -> {op["source"]}' if op['kind'] == 'link' else '') for op in operations]


def summary(operations):
    counts = Counter(op['kind'] for op in operations)
    return ', '.join(f'{count} {kind}' for kind, count in sorted(counts.items())) or 'Already applied'


@contextmanager
def installation_lock(home):
    path = safe_target(home, STATE / 'installation.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Conflict('Another installation or restore is running for this target home; retry when it finishes') from error
        yield
    finally:
        os.close(descriptor)


def execute(home, operations):
    """Serialize writers, recheck the plan, and roll back on exceptions."""
    if not operations:
        return None
    with installation_lock(home):
        return execute_locked(home, operations)


def execute_locked(home, operations):
    if len({op['path'] for op in operations}) != len(operations):
        raise Conflict('Multiple operations target the same path')
    for op in operations:
        target = safe_target(home, op['path'])
        if fingerprint(target) != op['before']:
            raise Conflict(f'Target changed after preflight: {target}')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    backup = safe_target(home, STATE / 'backups' / run_id)
    backup.mkdir(parents=True, mode=0o700)
    backup.chmod(0o700)
    completed = []
    try:
        for op in operations:
            target = safe_target(home, op['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            saved = backup / 'files' / op['path']
            if op['before'] is not None:
                saved.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, saved)
            completed.append(op)
            if op['kind'] == 'link':
                target.symlink_to(op['source'])
            elif op['kind'] == 'write':
                descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix='.' + target.name + '-')
                try:
                    with os.fdopen(descriptor, 'wb') as output:
                        output.write(op['content'])
                    os.chmod(temporary, op['mode'])
                    os.replace(temporary, target)
                finally:
                    if os.path.lexists(temporary):
                        os.unlink(temporary)
            elif op['kind'] != 'remove':
                raise Conflict(f'Unknown operation: {op["kind"]}')
        receipt = [{'path': op['path'], 'before': op['before'], 'after': fingerprint(home / op['path'])} for op in operations]
        (backup / 'receipt.json').write_bytes(json_bytes({'version': 1, 'home': str(home), 'operations': receipt}))
    except BaseException:
        for op in reversed(completed):
            target, saved = home / op['path'], backup / 'files' / op['path']
            if target.is_symlink() or target.is_file():
                target.unlink()
            if op['before'] is not None and os.path.lexists(saved):
                os.replace(saved, target)
        raise
    return backup


def restore(home, backup_id, dry_run=False):
    if dry_run:
        return restore_locked(home, backup_id, True)
    with installation_lock(home):
        return restore_locked(home, backup_id)


def restore_locked(home, backup_id, dry_run=False):
    if not re.fullmatch(r'\d{8}T\d{6}Z-[0-9a-f]{8}', backup_id):
        raise Conflict('Use a backup ID printed by apply')
    backup = safe_target(home, STATE / 'backups' / backup_id)
    receipt = read_json(backup / 'receipt.json')
    if not receipt or receipt.get('home') != str(home):
        raise Conflict('Backup does not belong to this target home')
    if (backup / 'restored').exists():
        raise Conflict('Backup was already restored')
    for op in receipt['operations']:
        target = safe_target(home, op['path'])
        if fingerprint(target) != op['after']:
            raise Conflict(f'Refusing to overwrite changes made after installation: {target}')
        if op['before'] is not None and not os.path.lexists(backup / 'files' / op['path']):
            raise Conflict(f'Missing backup: {op["path"]}')
    if dry_run:
        return
    for op in reversed(receipt['operations']):
        target = home / op['path']
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.exists():
            raise Conflict(f'Unexpected directory: {target}')
        if op['before'] is not None:
            os.replace(backup / 'files' / op['path'], target)
    (backup / 'restored').touch()


def skill_state(home):
    value = read_json(safe_target(home, STATE / 'skills.json'), {})
    if value and value.get('version') != 1:
        raise Conflict('Unsupported installed skill state version')
    return value


def legacy_lock_plan(home, adopt):
    path = safe_target(home, '.agents/.skill-lock.json')
    if not path.exists():
        return []
    if not adopt:
        raise Conflict('skills.sh still owns a source lock; use --adopt once to archive it and use skills.json')
    return [{'path': '.agents/.skill-lock.json', 'before': fingerprint(path), 'kind': 'remove'}]


def prepare(repo, home, profile, agents, adopt=False, additional_links=None):
    catalog = load_catalog(repo)
    desired = desired_links(repo, home, catalog, profile, agents)
    desired.update(additional_links or {})
    previous = skill_state(home)
    unexpected = unexpected_skills(home, set(desired) | set(previous.get('links', {})))
    if unexpected:
        raise Conflict('\n'.join(unexpected))
    operations = link_plan(home, desired, previous.get('links', {}), adopt)
    operations.extend(legacy_lock_plan(home, adopt))
    replacing = {op['path'] for op in operations if op['kind'] == 'link'}
    links = {rel: (source if rel in replacing else os.readlink(home / rel)) for rel, source in desired.items()}
    state = {'version': 1, 'repo': str(repo), 'profile': profile, 'agents': sorted(agents), 'links': links}
    operations.extend(write_plan(home, STATE / 'skills.json', json_bytes(state)))
    return operations, catalog, desired


def unexpected_skills(home, expected):
    problems = []
    for root in ['.agents/skills', '.claude/skills']:
        path = home / root
        if not path.exists():
            continue
        for entry in sorted(path.iterdir()):
            # Claude desktop owns this session-scoped cache of synchronized skills.
            if (root == '.claude/skills' and entry.name == 'synced' and entry.is_dir()
                    and not entry.is_symlink() and not (entry / 'SKILL.md').exists()):
                continue
            discovered = entry.is_symlink() or (entry.is_dir() and any(entry.rglob('SKILL.md')))
            if discovered and f'{root}/{entry.name}' not in expected:
                problems.append(f'Unexpected installed skill: {entry}; import/select it or move it outside discovery')
    return problems


def doctor(repo, home, profile, agents, additional_links=None, check_tools=True):
    catalog = load_catalog(repo)
    desired = desired_links(repo, home, catalog, profile, agents)
    desired.update(additional_links or {})
    problems = []
    for relative, source in desired.items():
        target = home / relative
        if not target.is_symlink() or target.resolve() != Path(source).resolve() or not target.exists():
            problems.append(f'Missing or incorrect link: {target}')
    previous = skill_state(home)
    if previous.get('profile') != profile or previous.get('repo') != str(repo) or previous.get('agents') != sorted(agents):
        problems.append('Installation receipt differs from the requested profile/repository/agents; run apply')
    for relative in previous.get('links', {}):
        if relative not in desired and os.path.lexists(home / relative):
            problems.append(f'Obsolete managed link: {home / relative}; run apply')
    problems.extend(unexpected_skills(home, desired))
    if (home / '.agents/.skill-lock.json').exists():
        problems.append('A skills.sh lock exists outside the versioned manifest; import the installation before adopting it')
    if check_tools:
        commands = {tool for key in select(catalog, profile) for tool in catalog['skills'][key].get('requires', [])}
        for command in sorted(commands):
            if not shutil.which(command):
                problems.append(f'Missing optional-profile command: {command}')
    return problems


def git_revision(repo):
    try:
        top = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL, text=True).strip()
        if Path(top) != repo:
            return 'not a Git checkout'
        head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', '--short', 'HEAD'], text=True).strip()
        dirty = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True).strip()
        return head + (' (uncommitted changes)' if dirty else '')
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 'not a Git checkout'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'list', 'apply', 'doctor', 'restore'])
    parser.add_argument('--profile', help='Named skill profile; defaults to installed profile or mac')
    parser.add_argument('--agents', nargs='+', choices=['codex', 'claude'])
    parser.add_argument('--target-home', type=Path, default=Path.home(), help='Explicit test target; does not change HOME')
    parser.add_argument('--adopt', action='store_true', help='Back up conflicting targets and archive the skills.sh lock')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--skip-tools', action='store_true', help='Check files only, useful for an isolated installation')
    parser.add_argument('--backup', help='Backup ID for restore')
    args = parser.parse_args(argv)
    home = args.target_home.expanduser().resolve()
    if args.command == 'restore':
        restore(home, args.backup or '', args.dry_run)
        print(('Would restore ' if args.dry_run else 'Restored ') + args.backup)
        return
    catalog = load_catalog()
    installed = skill_state(home)
    profile = args.profile or installed.get('profile', 'mac')
    agents = args.agents or installed.get('agents', ['codex', 'claude'])
    extra = {rel: source for rel, source in installed.get('links', {}).items() if rel in ENVIRONMENT_LINKS}
    if args.command == 'check':
        print(f'Valid: {len(catalog["skills"])} skills, {len(catalog["profiles"])} profiles')
    elif args.command == 'list':
        print('\n'.join(select(catalog, profile)))
    elif args.command == 'doctor':
        problems = doctor(REPO, home, profile, agents, extra, check_tools=not args.skip_tools)
        print(f'Skills: {git_revision(REPO)}; profile: {profile}')
        if problems:
            raise Conflict('\n'.join(problems))
        print('Links and selected tools match the manifest')
    else:
        operations, _, _ = prepare(REPO, home, profile, agents, args.adopt, extra)
        print(('\n'.join(describe(operations)) or 'Already applied') if args.dry_run else summary(operations))
        if not args.dry_run:
            backup = execute(home, operations)
            if backup:
                print(f'Backup: {backup.name}')


if __name__ == '__main__':
    try:
        main()
    except (Conflict, KeyError, ValueError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
