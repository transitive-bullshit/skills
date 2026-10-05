import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('x_mirror', ROOT / 'skills/x-mirror/x_mirror.py')
mirror = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mirror)


def bird_post(post_id='101', video=False):
    post = {'id': post_id, 'text': 'A public post', 'authorId': '327034465',
            'author': {'username': 'transitive_bs', 'name': 'Travis Fischer'}}
    if video:
        post['media'] = [{'type': 'video', 'url': 'https://example.com/thumbnail.jpg',
                          'videoUrl': 'https://example.com/video.mp4'}]
    return post


def fx_post(post_id='101', video=False):
    post = {'id': post_id, 'text': 'A public post',
            'author': {'id': '327034465', 'screen_name': 'transitive_bs'}}
    if video:
        post['media'] = {'videos': [{'type': 'video', 'url': 'https://example.com/video.mp4',
                                    'variants': [{'url': 'https://example.com/video.mp4',
                                                  'content_type': 'video/mp4', 'bitrate': 500}]}]}
    return {'code': 200, 'status': post}


class XLookupTests(unittest.TestCase):
    def test_local_reference_avoids_all_live_calls(self):
        post = {'id': '101', 'author_id': '327034465'}
        archive = Mock()
        archive.by_ids.return_value = [post]
        with patch.object(mirror, 'read_x_posts') as live:
            self.assertEqual(mirror.lookup_x_posts(archive, ['101']), {'101': post})
        live.assert_not_called()

    def test_only_archive_gaps_reach_live_transports(self):
        archive = Mock()
        archive.by_ids.return_value = [{'id': '101'}]
        with patch.object(mirror, 'read_x_posts', return_value={'102': None}) as live:
            self.assertEqual(mirror.lookup_x_posts(archive, ['101', '102']),
                             {'101': {'id': '101'}, '102': None})
        live.assert_called_once_with(['102'])

    def test_bird_success_stops_before_fxtwitter_and_paid_api(self):
        with patch.object(mirror, 'cli_json', return_value=bird_post()) as cli, \
                patch.object(mirror, 'fxtwitter_post') as fx:
            post = mirror.read_x_posts(['101'])['101']
        self.assertEqual(post['author_id'], '327034465')
        self.assertEqual(post['_username'], 'transitive_bs')
        self.assertEqual(cli.call_count, 1)
        self.assertEqual(cli.call_args.args[0], 'bird')
        fx.assert_not_called()

    def test_missing_bird_uses_fxtwitter_without_paid_api(self):
        with patch.object(mirror, 'cli_json', side_effect=FileNotFoundError('bird')) as cli, \
                patch.object(mirror, 'fxtwitter_post', return_value=fx_post()) as fx:
            post = mirror.read_x_posts(['101'])['101']
        self.assertEqual(post['author_id'], '327034465')
        self.assertEqual(cli.call_count, 1)
        fx.assert_called_once_with('101')

    def test_malformed_bird_response_uses_the_next_free_source(self):
        with patch.object(mirror, 'cli_json', return_value=[]) as cli, \
                patch.object(mirror, 'fxtwitter_post', return_value=fx_post()) as fx:
            self.assertIsNotNone(mirror.read_x_posts(['101'])['101'])
        self.assertEqual(cli.call_count, 1)
        fx.assert_called_once_with('101')

    def test_missing_video_field_falls_through_a_successful_bird_read(self):
        with patch.object(mirror, 'cli_json', return_value=bird_post()) as cli, \
                patch.object(mirror, 'fxtwitter_post', return_value=fx_post(video=True)) as fx:
            variants = mirror.x_video_variants('101')
        self.assertEqual(variants[0]['url'], 'https://example.com/video.mp4')
        self.assertEqual(variants[0]['bit_rate'], 500)
        self.assertEqual(cli.call_count, 1)
        fx.assert_called_once_with('101')

    def test_native_bird_video_url_is_sufficient(self):
        with patch.object(mirror, 'cli_json', return_value=bird_post(video=True)), \
                patch.object(mirror, 'fxtwitter_post') as fx:
            variants = mirror.x_video_variants('101')
        self.assertEqual(variants, [{'url': 'https://example.com/video.mp4',
                                     'content_type': 'video/mp4', 'bit_rate': 0}])
        fx.assert_not_called()

    def test_paid_reads_batch_only_unresolved_ids_after_both_free_failures(self):
        calls = []

        def cli(*args, **kwargs):
            calls.append(args)
            if args[0] == 'bird':
                if args[4] == '101':
                    return bird_post()
                raise RuntimeError('bird unavailable')
            return {'data': [{'id': i, 'author_id': '327034465'} for i in ['102', '103']],
                    'includes': {'users': [{'id': '327034465', 'username': 'transitive_bs'}]}}

        with patch.object(mirror, 'cli_json', side_effect=cli), \
                patch.object(mirror, 'fxtwitter_post', side_effect=OSError('public API unavailable')) as fx, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            posts = mirror.read_x_posts(['101', '102', '103', '102'])
        self.assertTrue(all(posts.values()))
        self.assertEqual([c[0] for c in calls], ['bird', 'bird', 'bird', 'xurl'])
        self.assertIn('ids=102,103&', calls[-1][1])
        self.assertEqual([c.args[0] for c in fx.call_args_list], ['102', '103'])
        self.assertIn('paid xurl fallback', output.getvalue())

    def test_all_failures_leave_reference_pending(self):
        with patch.object(mirror, 'cli_json', side_effect=RuntimeError('unavailable')), \
                patch.object(mirror, 'fxtwitter_post', return_value={'code': 404, 'status': None}), \
                contextlib.redirect_stdout(io.StringIO()):
            lookup = mirror.read_x_posts(['101'])
        self.assertEqual(lookup, {'101': None})
        _, decision = mirror.resolve_x_refs(['101'], 'bluesky', lookup, {}, Mock())
        self.assertEqual(decision[0], 'wait')

    def test_local_video_variants_preserve_media_without_live_lookup(self):
        post = {'id': '101', 'attachments': {'media_keys': ['m1']}}
        media = {'m1': {'type': 'video', 'variants': [
            {'content_type': 'video/mp4', 'bit_rate': 10, 'url': 'https://example.com/small.mp4'},
            {'content_type': 'video/mp4', 'bit_rate': 20, 'url': 'https://example.com/large.mp4'}]}}
        with patch.object(mirror, 'x_video_variants') as live, \
                patch.object(mirror.urllib.request, 'urlretrieve') as download:
            files = mirror.media_files(post, media, '/private/tmp')
        self.assertEqual(files, [Path('/private/tmp/101_0.mp4')])
        download.assert_called_once_with('https://example.com/large.mp4', files[0])
        live.assert_not_called()

    def test_invalid_identifier_never_reaches_a_provider(self):
        with patch.object(mirror, 'cli_json') as cli, patch.object(mirror, 'fxtwitter_post') as fx:
            with self.assertRaises(ValueError):
                mirror.read_x_posts(['101/../../private'])
        cli.assert_not_called()
        fx.assert_not_called()


if __name__ == '__main__':
    unittest.main()
