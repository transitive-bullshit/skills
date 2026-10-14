"""Exercise review state and output boundaries without launching a model."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'skills/codex/scripts/review-status.py'
spec = importlib.util.spec_from_file_location('review_status', SOURCE)
review_status = importlib.util.module_from_spec(spec)
previous_bytecode_setting = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    spec.loader.exec_module(review_status)
finally:
    sys.dont_write_bytecode = previous_bytecode_setting


class ReviewStatusTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.events = self.directory / 'events.jsonl'
        self.events.write_text(json.dumps({'type': 'turn.completed'}) + '\n')
        (self.directory / 'exit-code').write_text('0\n')
        (self.directory / 'verdict.md').write_text('A finding that needs triage.\n')

    def test_completion_requires_all_receipts_and_does_not_interpret_findings(self):
        self.assertEqual(review_status.status(self.directory)['state'], 'complete')
        for receipt in ['exit-code', 'events.jsonl', 'verdict.md']:
            with self.subTest(receipt=receipt):
                path = self.directory / receipt
                original = path.read_bytes()
                path.unlink()
                self.assertNotEqual(review_status.status(self.directory)['state'], 'complete')
                path.write_bytes(original)
        (self.directory / 'verdict.md').write_text(' \n\t')
        self.assertFalse(review_status.status(self.directory)['verdict_present'])

    def test_active_partial_record_is_deferred_but_exited_corruption_is_visible(self):
        (self.directory / 'exit-code').unlink()
        self.events.write_text('{"type":"turn.started"}\n{"type":"item.')
        active = review_status.status(self.directory)
        self.assertEqual(active['state'], 'active')
        self.assertTrue(active['pending_record'])
        self.assertEqual(active['parse_errors'], 0)
        (self.directory / 'exit-code').write_text('0')
        exited = review_status.status(self.directory)
        self.assertEqual(exited['state'], 'incomplete')
        self.assertEqual(exited['parse_errors'], 1)
        self.assertIn('line 2', exited['issues'][0])
        self.events.write_text('bad record\n{"type":"turn.completed"}\n')
        self.assertEqual(review_status.status(self.directory)['state'], 'incomplete')

    def test_failure_and_unknown_exit_never_complete(self):
        for events, exit_code, expected in [
            ([{'type': 'turn.failed', 'error': {'message': 'Request failed'}}], '0', 'failed'),
            ([{'type': 'turn.completed'}], '2', 'failed'),
            ([{'type': 'turn.completed'}], None, 'incomplete'),
            ([{'type': 'turn.completed'}], 'invalid', 'incomplete'),
            ([{'type': 'turn.started'}], '0', 'incomplete'),
            ([{'type': 'turn.completed'}], '9' * 3000, 'incomplete'),
            ([{'type': 'turn.completed'}], '256', 'incomplete'),
            ([{'type': 'item.completed', 'item': {'type': 'command_execution',
               'exit_code': True}}, {'type': 'turn.completed'}], '0', 'incomplete'),
            ([{'type': 'item.completed', 'item': {'type': 'command_execution',
               'exit_code': int('9' * 3000)}}, {'type': 'turn.completed'}], '0', 'incomplete'),
            ([{'type': 'turn.completed'}, {'type': 'turn.started'}], '0', 'incomplete'),
        ]:
            with self.subTest(events=events, exit_code=exit_code):
                self.events.write_text(''.join(json.dumps(event) + '\n' for event in events))
                path = self.directory / 'exit-code'
                if exit_code is None:
                    path.unlink()
                else:
                    path.write_text(exit_code)
                self.assertEqual(review_status.status(self.directory)['state'], expected)

    def test_megabyte_payload_stays_in_artifacts(self):
        payload = 'PRIVATE_OUTPUT_MARKER' * 60000
        event = {'type': 'item.completed', 'item': {'type': 'command_execution',
                 'command': 'check ' + 'x' * 10000, 'status': 's' * 32 + 'STATUS_PAYLOAD' * 10000,
                 'exit_code': 0, 'aggregated_output': payload}}
        self.events.write_text(json.dumps(event) + '\n{"type":"turn.completed"}\n'
                               + json.dumps({'type': 'x' * 64 + 'EVENT_PAYLOAD' * 10000}) + '\n')
        (self.directory / 'stderr.log').write_text('error ' + 'x' * 10000 + '\n')
        result = subprocess.run([sys.executable, str(SOURCE), str(self.directory)],
                                capture_output=True, text=True, check=True)
        self.assertLessEqual(len(result.stdout.encode('utf-8')), review_status.MAX_OUTPUT_BYTES)
        self.assertNotIn('PRIVATE_OUTPUT_MARKER', result.stdout)
        self.assertNotIn('STATUS_PAYLOAD', result.stdout)
        self.assertNotIn('EVENT_PAYLOAD', result.stdout)
        self.assertNotIn('A finding that needs triage', result.stdout)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed['state'], 'complete')
        self.assertEqual(parsed['last_command']['exit_code'], 0)
        self.assertIsNone(parsed['error'])
        self.assertTrue(parsed['stderr_tail'].startswith('x'))
        self.assertEqual(parsed['artifacts']['verdict'], str((self.directory / 'verdict.md').resolve()))

    def test_escaped_text_cannot_exceed_output_cap_or_claim_completion(self):
        self.events.write_text(json.dumps({'type': 'item.completed', 'item': {
            'type': 'error', 'message': '\0' * 10000}}) + '\n{"type":"turn.completed"}\n')
        (self.directory / 'stderr.log').write_text('\0' * 10000)
        result = subprocess.run([sys.executable, str(SOURCE), str(self.directory)],
                                capture_output=True, text=True, check=True)
        self.assertLessEqual(len(result.stdout.encode('utf-8')), review_status.MAX_OUTPUT_BYTES)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed['state'], 'incomplete')
        self.assertIn('exceeds', parsed['issues'][0])


if __name__ == '__main__':
    unittest.main()
