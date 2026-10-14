#!/usr/bin/env python3
"""Print compact review progress; the verdict and command output stay in their files."""
import argparse
import json
from pathlib import Path


MAX_OUTPUT_BYTES = 2048


def short(value, limit=160):
    if not isinstance(value, str):
        return None
    return value if len(value) <= limit else value[:limit] + '…'


def status(directory):
    paths = {name: directory / filename for name, filename in {
        'events': 'events.jsonl', 'stderr': 'stderr.log',
        'verdict': 'verdict.md', 'exit_code': 'exit-code',
    }.items()}
    result = {
        'state': 'active', 'exit_code': None, 'last_event': None,
        'turn_completed': False, 'turn_failed': False, 'verdict_present': False,
        'last_command': None, 'error': None, 'stderr_tail': None, 'parse_errors': 0,
        'pending_record': False, 'issues': [],
        'artifacts': {name: str(path) for name, path in paths.items()},
    }

    def issue(message):
        if len(result['issues']) < 4:
            result['issues'].append(short(message))

    if paths['exit_code'].exists():
        try:
            value = paths['exit_code'].read_text().strip()
            if not (value.isascii() and value.isdigit() and len(value) <= 3 and int(value) <= 255):
                raise ValueError('Expected shell exit status 0..255')
            result['exit_code'] = int(value)
        except (OSError, ValueError) as error:
            issue('Invalid exit-code record: ' + str(error))
    try:
        with paths['events'].open('rb') as events:
            for number, line in enumerate(events, 1):
                if not line.endswith(b'\n') and result['exit_code'] is None:
                    result['pending_record'] = True
                    break
                try:
                    event = json.loads(line)
                    if not isinstance(event, dict) or not isinstance(event.get('type'), str):
                        raise ValueError('Expected an event object with a type')
                except (UnicodeDecodeError, ValueError) as error:
                    result['parse_errors'] += 1
                    issue(f'Invalid event at line {number}: {error}')
                    continue
                kind = event['type']
                result['last_event'] = short(kind, 64)
                if kind == 'turn.started':
                    result['turn_completed'] = False
                elif kind == 'turn.completed':
                    result['turn_completed'] = True
                elif kind == 'turn.failed':
                    result['turn_failed'] = True
                    error = event.get('error')
                    result['error'] = short(error.get('message') if isinstance(error, dict) else error)
                elif kind == 'error':
                    result['error'] = short(event.get('message'))
                item = event.get('item')
                if not isinstance(item, dict):
                    continue
                if item.get('type') == 'command_execution':
                    exit_code = item.get('exit_code')
                    if exit_code is not None and (type(exit_code) is not int or not 0 <= exit_code <= 255):
                        issue('Invalid command exit status at line ' + str(number))
                        exit_code = None
                    result['last_command'] = {
                        'command': short(item.get('command')),
                        'status': short(item.get('status'), 32),
                        'exit_code': exit_code,
                    }
                elif item.get('type') == 'error':
                    result['error'] = short(item.get('message'))
    except OSError as error:
        issue('Cannot read events: ' + str(error))
    try:
        with paths['verdict'].open('rb') as verdict:
            result['verdict_present'] = any(chunk.strip() for chunk in iter(lambda: verdict.read(4096), b''))
    except FileNotFoundError:
        pass
    except OSError as error:
        issue('Cannot read verdict: ' + str(error))
    try:
        with paths['stderr'].open('rb') as stderr:
            stderr.seek(0, 2)
            stderr.seek(max(0, stderr.tell() - 4096))
            lines = stderr.read().decode('utf-8', errors='replace').splitlines()
            result['stderr_tail'] = short(next((line for line in reversed(lines) if line.strip()), None))
    except FileNotFoundError:
        pass
    except OSError as error:
        issue('Cannot read stderr: ' + str(error))
    if result['turn_failed'] or result['exit_code'] not in (None, 0):
        result['state'] = 'failed'
    elif (result['exit_code'] == 0 and result['turn_completed']
          and result['verdict_present'] and not result['pending_record']
          and not result['parse_errors'] and not result['issues']):
        result['state'] = 'complete'
    elif result['exit_code'] is not None or result['turn_completed'] or result['issues']:
        result['state'] = 'incomplete'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Review artifact directory')
    args = parser.parse_args()
    result = status(args.directory.resolve())
    output = json.dumps(result)
    if len(output.encode('utf-8')) + 1 > MAX_OUTPUT_BYTES:
        # Unusual path lengths or escaped text must not turn monitoring into a log dump.
        output = json.dumps({
            'state': 'failed' if result['state'] == 'failed' else 'incomplete',
            'exit_code': result['exit_code'], 'turn_completed': result['turn_completed'],
            'turn_failed': result['turn_failed'], 'verdict_present': result['verdict_present'],
            'issues': ['Status exceeds 2048 bytes; inspect files in the supplied review directory.'],
        })
    print(output)


if __name__ == '__main__':
    main()
