"""Check that provenance patches preserve real resource changes and reject drift."""
import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/upstream.py'
spec = importlib.util.spec_from_file_location('upstream', SOURCE)
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)


class UpstreamTests(unittest.TestCase):
    def test_binary_deletion_executable_and_local_resources_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            pristine, effective = repo / 'pristine', repo / 'effective'
            pristine.mkdir()
            effective.mkdir()
            for directory in [pristine, effective]:
                (directory / 'SKILL.md').write_text('Original instructions\n')
            (pristine / 'obsolete.txt').write_text('Removed upstream resource\n')
            (pristine / 'asset.bin').write_bytes(b'\0old\x01')
            (effective / 'asset.bin').write_bytes(b'\0new\x02')
            (effective / 'run.sh').write_text('#!/bin/sh\nexit 0\n')
            (effective / 'run.sh').chmod(0o755)
            (effective / 'SKILL.md').write_text('Locally adapted instructions\n')
            record = {'path': 'effective', 'origin': {'commit': 'a' * 40},
                      'upstream': {'snapshot': 'pristine', 'patch': 'patches/local.patch'}}
            upstream.process(repo, record, write=True)
            upstream.process(repo, record)
            (effective / 'SKILL.md').write_text('Unrecorded drift\n')
            with self.assertRaisesRegex(ValueError, 'does not reproduce'):
                upstream.process(repo, record)

    def test_snapshot_and_patch_tampering_are_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            for name in ['pristine', 'effective']:
                (repo / name).mkdir()
                (repo / name / 'SKILL.md').write_text('Same instructions\n')
            record = {'path': 'effective', 'origin': {'commit': 'b' * 40},
                      'upstream': {'snapshot': 'pristine', 'patch': 'local.patch'}}
            upstream.process(repo, record, write=True)
            upstream.process(repo, record)
            record['upstream']['snapshotSha256'] = 'wrong'
            with self.assertRaisesRegex(ValueError, 'Recorded hash differs'):
                upstream.process(repo, record)
            with self.assertRaisesRegex(ValueError, 'inside repository'):
                upstream.inside(repo, '../outside')

    def test_resource_and_symlink_renames_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            for name in ['pristine', 'effective']:
                (repo / name).mkdir()
                (repo / name / 'SKILL.md').write_text('Unchanged instructions\n')
            (repo / 'pristine/old.txt').write_text('Unchanged resource contents\n')
            (repo / 'effective/new.txt').write_text('Unchanged resource contents\n')
            (repo / 'pristine/old-link').symlink_to('SKILL.md')
            (repo / 'effective/new-link').symlink_to('SKILL.md')
            record = {'path': 'effective', 'origin': {'commit': 'c' * 40},
                      'upstream': {'snapshot': 'pristine', 'patch': 'local.patch'}}
            upstream.process(repo, record, write=True)
            upstream.process(repo, record)

    def test_invalid_batch_does_not_partially_replace_patches(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / 'scripts').mkdir()
            shutil.copy2(SOURCE, repo / 'scripts/upstream.py')
            for name in ['pristine', 'effective']:
                (repo / name).mkdir()
                (repo / name / 'SKILL.md').write_text('Original instructions\n')
            record = {'path': 'effective', 'origin': {'kind': 'adopted', 'commit': 'd' * 40},
                      'upstream': {'snapshot': 'pristine', 'patch': 'local.patch'}}
            upstream.process(repo, record, write=True)
            manifest = {'skills': {'valid': record, 'invalid': {'origin': {}}}}
            manifest_path = repo / 'skills.json'
            manifest_path.write_text(json.dumps(manifest))
            before = manifest_path.read_bytes(), (repo / 'local.patch').read_bytes()
            (repo / 'effective/SKILL.md').write_text('Intentional new local change\n')
            result = subprocess.run([sys.executable, str(repo / 'scripts/upstream.py'),
                                     'record', 'valid', 'invalid'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, (manifest_path.read_bytes(), (repo / 'local.patch').read_bytes()))


class DerivedUpstreamTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.skill = self.repo / 'combined'
        source = self.skill / 'sources/original'
        source.mkdir(parents=True)
        self.source_file = source / 'SKILL.upstream.md'
        self.source_file.write_text('Original upstream instructions\n')
        self.personal = self.skill / 'personal.md'
        self.personal.write_text('Choose checks proportionate to risk.\n')
        self.output = self.skill / 'SKILL.md'
        self.output.write_text('Synthesized testing instructions\n')
        self.lock_path = self.skill / 'sources.lock.json'
        source_blob = subprocess.run(
            ['git', 'hash-object', '--stdin'], input=self.source_file.read_bytes(),
            capture_output=True, check=True).stdout.decode().strip()
        lock = {
            'version': 1,
            'sources': [{
                'commit': 'e' * 40,
                'root': 'sources/original',
                'files': [{
                    'path': 'SKILL.upstream.md',
                    'sha256': self.sha256(self.source_file),
                    'gitBlob': source_blob,
                    'gitMode': '100644',
                }],
            }],
            'personalInputs': [{'path': 'personal.md', 'sha256': self.sha256(self.personal)}],
            'outputs': [{'path': 'SKILL.md', 'sha256': self.sha256(self.output)}],
        }
        self.lock_path.write_text(json.dumps(lock, indent=2) + '\n')
        self.record = {'path': 'combined', 'origin': {'kind': 'derived'},
                       'derivation': {'lock': 'sources.lock.json'}}

    @staticmethod
    def sha256(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def assert_check_and_record_reject(self, message):
        before = self.lock_path.read_bytes()
        for write in [False, True]:
            with self.subTest(write=write):
                with self.assertRaisesRegex(ValueError, message):
                    upstream.process(self.repo, self.record, write=write)
                self.assertEqual(before, self.lock_path.read_bytes())

    def test_synthesized_output_edits_are_recordable_without_changing_inputs(self):
        upstream.process(self.repo, self.record)
        before = json.loads(self.lock_path.read_text())
        source_bytes, personal_bytes = self.source_file.read_bytes(), self.personal.read_bytes()
        self.output.write_text('Reviewed improvement to the synthesized instructions\n')
        with self.assertRaisesRegex(ValueError, 'Derived output changed'):
            upstream.process(self.repo, self.record)

        upstream.process(self.repo, self.record, write=True)
        upstream.process(self.repo, self.record)

        after = json.loads(self.lock_path.read_text())
        self.assertEqual(before['sources'], after['sources'])
        self.assertEqual(before['personalInputs'], after['personalInputs'])
        self.assertEqual(source_bytes, self.source_file.read_bytes())
        self.assertEqual(personal_bytes, self.personal.read_bytes())
        self.assertEqual(after['outputs'][0]['sha256'], self.sha256(self.output))
        self.assertNotEqual(before['outputs'][0]['sha256'], after['outputs'][0]['sha256'])

    def test_record_cannot_accept_pinned_source_content_or_mode_drift(self):
        original = self.source_file.read_bytes()
        for drift in ['content', 'executable mode']:
            with self.subTest(drift=drift):
                self.source_file.write_bytes(original)
                self.source_file.chmod(0o644)
                if drift == 'content':
                    self.source_file.write_text('Unreviewed upstream replacement\n')
                else:
                    self.source_file.chmod(0o755)
                self.output.write_text('An otherwise recordable output edit\n')
                self.assert_check_and_record_reject('Pinned source changed')

    def test_record_cannot_accept_personal_input_drift(self):
        self.personal.write_text('Different personal policy\n')
        self.output.write_text('An otherwise recordable output edit\n')
        self.assert_check_and_record_reject('Personal input changed')

    def test_unlisted_source_file_is_rejected(self):
        (self.source_file.parent / 'unrecorded.md').write_text('Unexpected source instructions\n')
        self.assert_check_and_record_reject('Unrecorded or missing source files')

    def test_missing_source_file_is_rejected(self):
        self.source_file.unlink()
        self.assert_check_and_record_reject('Source must be a regular file')

    def test_invalid_mixed_batch_preserves_earlier_lock_patch_and_manifest(self):
        (self.repo / 'scripts').mkdir()
        shutil.copy2(SOURCE, self.repo / 'scripts/upstream.py')
        for name in ['pristine', 'effective']:
            (self.repo / name).mkdir()
            (self.repo / name / 'SKILL.md').write_text('Original adopted instructions\n')
        adopted = {'path': 'effective', 'origin': {'kind': 'adopted', 'commit': 'f' * 40},
                   'upstream': {'snapshot': 'pristine', 'patch': 'adopted.patch'}}
        upstream.process(self.repo, adopted, write=True)
        shutil.copytree(self.skill, self.repo / 'invalid')
        invalid = {'path': 'invalid', 'origin': {'kind': 'derived'},
                   'derivation': {'lock': 'sources.lock.json'}}
        manifest_path = self.repo / 'skills.json'
        manifest_path.write_text(json.dumps({'skills': {
            'adopted': adopted, 'combined': self.record, 'invalid': invalid}}))
        protected = [manifest_path, self.repo / 'adopted.patch', self.lock_path,
                     self.repo / 'invalid/sources.lock.json']
        before = {path: path.read_bytes() for path in protected}
        (self.repo / 'effective/SKILL.md').write_text('Reviewed adopted edit\n')
        self.output.write_text('Reviewed derived edit\n')
        (self.repo / 'invalid/sources/original/SKILL.upstream.md').write_text('Unreviewed source\n')

        result = subprocess.run([
            sys.executable, str(self.repo / 'scripts/upstream.py'),
            'record', 'adopted', 'combined', 'invalid'], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid: Pinned source changed', result.stderr)
        self.assertEqual(before, {path: path.read_bytes() for path in protected})
