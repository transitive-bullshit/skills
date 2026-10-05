"""Exercise the installer's public CLI against disposable user directories."""
import importlib.util
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/skillset.py'


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name).resolve()
        self.repo, self.home = self.root / 'skills', self.root / 'home'
        (self.repo / 'scripts').mkdir(parents=True)
        self.home.mkdir()
        shutil.copy2(SOURCE, self.repo / 'scripts/skillset.py')
        self.manifest = {'version': 1, 'skills': {}, 'profiles': {'mac': {'skills': ['alpha', 'beta']}, 'cloud': {'skills': ['alpha']}}}
        for name in ['alpha', 'beta']:
            directory = self.repo / 'skills' / name
            directory.mkdir(parents=True)
            (directory / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Test {name}\n---\nUse references/example.md\n')
            (directory / 'references').mkdir()
            (directory / 'references/example.md').write_text('Referenced content\n')
            self.manifest['skills'][name] = {'path': 'skills/' + name, 'origin': {'kind': 'personal'}, 'requires': []}
        self.save_manifest()

    def save_manifest(self):
        (self.repo / 'skills.json').write_text(json.dumps(self.manifest))

    def cli(self, *args, success=True):
        result = subprocess.run([sys.executable, str(self.repo / 'scripts/skillset.py'), *args,
                                 '--target-home', str(self.home), '--skip-tools'], capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_shared_editable_files_and_idempotence(self):
        self.cli('apply')
        shared = self.home / '.agents/skills/alpha'
        claude = self.home / '.claude/skills/alpha'
        self.assertTrue(shared.is_symlink())
        self.assertEqual(claude.resolve(), self.repo / 'skills/alpha')
        self.assertEqual((claude / 'references/example.md').read_text(), 'Referenced content\n')
        with (shared / 'SKILL.md').open('a') as output:
            output.write('Local edit\n')
        self.assertIn('Local edit', (self.repo / 'skills/alpha/SKILL.md').read_text())
        self.assertIn('Already applied', self.cli('apply').stdout)
        self.cli('doctor')
        self.assertEqual(len(list((self.home / '.local/state/agent-env/backups').iterdir())), 1)

    def test_entire_plan_preflights_before_any_mutation(self):
        conflict = self.home / '.agents/skills/beta'
        conflict.mkdir(parents=True)
        (conflict / 'SKILL.md').write_text('Keep this local version')
        result = self.cli('apply', success=False)
        self.assertIn('Unmanaged target', result.stderr)
        self.assertFalse(os.path.lexists(self.home / '.agents/skills/alpha'))
        self.assertFalse((self.home / '.local').exists())
        self.assertEqual((conflict / 'SKILL.md').read_text(), 'Keep this local version')

    def test_adoption_archives_lock_and_can_be_restored(self):
        old = self.home / '.agents/skills/beta'
        old.mkdir(parents=True)
        (old / 'SKILL.md').write_text('Original local skill\n')
        lock = self.home / '.agents/.skill-lock.json'
        lock.write_text('{"old": "source lock"}\n')
        result = self.cli('apply', '--adopt')
        backup_id = result.stdout.split('Backup: ')[1].strip()
        backup = self.home / '.local/state/agent-env/backups' / backup_id
        self.assertEqual(backup.stat().st_mode & 0o777, 0o700)
        self.assertFalse(lock.exists())
        self.assertTrue(old.is_symlink())
        self.assertEqual((backup / 'files/.agents/skills/beta/SKILL.md').read_text(), 'Original local skill\n')
        self.cli('restore', '--backup', backup_id)
        self.assertFalse(old.is_symlink())
        self.assertEqual((old / 'SKILL.md').read_text(), 'Original local skill\n')
        self.assertTrue(lock.exists())
        self.assertFalse(os.path.lexists(self.home / '.agents/skills/alpha'))

    def test_profile_switch_removes_only_owned_links(self):
        self.cli('apply')
        system = self.home / '.codex/skills/.system/native/SKILL.md'
        system.parent.mkdir(parents=True)
        system.write_text('Host-owned system skill')
        self.cli('apply', '--profile', 'cloud', '--agents', 'codex')
        self.assertFalse(os.path.lexists(self.home / '.agents/skills/beta'))
        self.assertFalse(os.path.lexists(self.home / '.claude/skills/alpha'))
        self.assertTrue((self.home / '.agents/skills/alpha').is_symlink())
        self.assertEqual(system.read_text(), 'Host-owned system skill')
        self.cli('doctor')

    def test_unknown_installation_is_reported_and_preserved(self):
        extra = self.home / '.agents/skills/unregistered'
        extra.mkdir(parents=True)
        (extra / 'SKILL.md').write_text('Experimental skill')
        self.assertIn('Unexpected installed skill', self.cli('apply', '--adopt', success=False).stderr)
        self.assertEqual((extra / 'SKILL.md').read_text(), 'Experimental skill')
        self.assertFalse(os.path.lexists(self.home / '.agents/skills/alpha'))

    def test_claude_synced_cache_remains_host_owned(self):
        cached = self.home / '.claude/skills/synced/session/docx/SKILL.md'
        cached.parent.mkdir(parents=True)
        cached.write_text('Claude desktop synchronized skill')
        self.cli('apply')
        self.cli('doctor')
        self.cli('apply', '--profile', 'cloud', '--agents', 'codex')
        self.cli('doctor')
        self.assertEqual(cached.read_text(), 'Claude desktop synchronized skill')
        self.assertFalse((self.home / '.claude/skills/synced').is_symlink())

    def test_synced_name_does_not_hide_standalone_skills(self):
        for root in ['.agents/skills', '.claude/skills']:
            with self.subTest(root=root):
                extra = self.home / root / 'synced'
                extra.mkdir(parents=True)
                (extra / 'SKILL.md').write_text('Unregistered standalone skill')
                self.assertIn('Unexpected installed skill', self.cli('apply', success=False).stderr)
                shutil.rmtree(extra)
                extra.symlink_to(self.repo / 'skills/alpha')
                self.assertIn('Unexpected installed skill', self.cli('apply', success=False).stderr)
                extra.unlink()

    def test_changed_owned_link_is_not_pruned(self):
        self.cli('apply')
        target = self.home / '.agents/skills/beta'
        target.unlink()
        other = self.root / 'other'
        other.mkdir()
        target.symlink_to(other)
        result = self.cli('apply', '--profile', 'cloud', success=False)
        self.assertIn('Changed managed target', result.stderr)
        self.assertEqual(target.resolve(), other)

    def test_unregistered_and_nested_skill_roots_fail_validation(self):
        extra = self.repo / 'skills/extra'
        extra.mkdir()
        self.assertIn('Unregistered', self.cli('check', success=False).stderr)
        extra.rmdir()
        nested = self.repo / 'skills/alpha/nested/SKILL.md'
        nested.parent.mkdir()
        nested.write_text('Duplicate root')
        self.assertIn('nested skill root', self.cli('check', success=False).stderr)

    def test_wrong_name_and_profile_cycle_fail_validation(self):
        skill = self.repo / 'skills/alpha/SKILL.md'
        text = skill.read_text()
        skill.write_text(text.replace('name: alpha', 'name: beta'))
        self.assertIn('name must match', self.cli('check', success=False).stderr)
        skill.write_text(text)
        self.manifest['profiles']['mac']['extends'] = ['cloud']
        self.manifest['profiles']['cloud']['extends'] = ['mac']
        self.save_manifest()
        self.assertIn('Profile cycle', self.cli('check', success=False).stderr)

    def test_symlinked_installation_parent_is_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.home / '.agents').symlink_to(outside)
        self.assertIn('parent must be a directory', self.cli('apply', success=False).stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_io_failure_rolls_back_prior_operations(self):
        spec = importlib.util.spec_from_file_location('skillset_test', SOURCE)
        lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lib)
        target = self.home / '.agents/skills/alpha'
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('Keep original')
        operations, _, _ = lib.prepare(self.repo, self.home, 'mac', ['codex'], adopt=True)
        original = Path.symlink_to

        def fail_beta(path, *args, **kwargs):
            if path.name == 'beta':
                raise OSError('Simulated disk failure')
            return original(path, *args, **kwargs)

        with patch.object(Path, 'symlink_to', fail_beta):
            with self.assertRaises(OSError):
                lib.execute(self.home, operations)
        self.assertFalse(target.is_symlink())
        self.assertEqual((target / 'SKILL.md').read_text(), 'Keep original')
        self.assertFalse(os.path.lexists(self.home / '.agents/skills/beta'))
        self.assertFalse((self.home / '.local/state/agent-env/skills.json').exists())

    def test_dry_run_does_not_create_target(self):
        self.cli('apply', '--dry-run')
        self.assertEqual(list(self.home.iterdir()), [])

    def test_concurrent_installer_is_refused_before_changing_links(self):
        lock = self.home / '.local/state/agent-env/installation.lock'
        lock.parent.mkdir(parents=True)
        with lock.open('w') as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            result = self.cli('apply', success=False)
            self.assertIn('Another installation or restore', result.stderr)
        self.assertFalse((self.home / '.agents').exists())


if __name__ == '__main__':
    unittest.main()
