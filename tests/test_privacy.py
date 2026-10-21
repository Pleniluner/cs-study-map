import json
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cs_study_map.privacy import private_reference
from cs_study_map.sync import changes_between, make_records
from cs_study_map.storage import StudyError
from cs_study_map.validate import audit_tracked


class PrivacyTests(unittest.TestCase):
    def test_publication_blocks_custom_drive_paths_and_contact_addresses(self):
        for value in ['Q:' + '/custom-materials/notes', 'student' + '@' + 'example.test']:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / 'docs').mkdir()
                (root / 'docs/README.md').write_text(value, encoding='utf-8')
                with patch('cs_study_map.validate.subprocess.run', return_value=SimpleNamespace(stdout=b'docs/README.md\0')), patch('cs_study_map.validate.read_jsonl', return_value=[]):
                    with self.assertRaises(StudyError):
                        audit_tracked(root)

    def test_plain_and_encoded_private_references(self):
        address = 'student' + '@' + 'example.test'
        for value in [address, address.replace('@', '%40'), 'Z:' + '/course-notes', '/home/' + 'student/notes', 'file:///' + 'notes']:
            with self.subTest(value=value):
                self.assertTrue(private_reference(value))
        self.assertFalse(private_reference('https://github.com/example/project/blob/main/course/README.md'))
        self.assertFalse(private_reference('docs/early-work/README.md'))

    def test_sync_excludes_contacts_and_change_log_does_not_repeat_them(self):
        private = 'course/' + 'student' + '@' + 'example.test' + '/notes.md'
        entries = [{'path': p, 'type': 'blob', 'mode': '100644', 'sha': 'a' * 40, 'size': 10}
                   for p in [private, 'course/README.md']]
        project = {'courses': [], 'source': {'max_download_bytes': 100}}
        records = make_records(entries, project)
        self.assertEqual([r['path'] for r in records], ['course/README.md'])
        previous = [{'path': private, 'blob_sha': 'a' * 40}, *records]
        self.assertEqual(changes_between(previous, records), {'added': [], 'removed': [], 'modified': [], 'moved': []})

    def test_json_program_newlines_do_not_hide_private_strings(self):
        code = '\n'.join(['n = 2', 'while n:', '    n = n - 1'])
        public = json.dumps({'program': {'code': code, 'output': ''}})
        self.assertFalse(private_reference(public, json_document=True))
        private_values = ['Q:' + '/notes', 'Q:' + chr(92) + 'notes',
                          'Q%3A' + '%2Fnotes', 'student' + '@' + 'example.test']
        for value in private_values:
            with self.subTest(kind='value'):
                self.assertTrue(private_reference(json.dumps({'safe': [value]}), json_document=True))
            with self.subTest(kind='key'):
                self.assertTrue(private_reference(json.dumps({value: 'safe'}), json_document=True))
        duplicate = '{"value": ' + json.dumps(private_values[0]) + ', "value": "safe"}'
        self.assertTrue(private_reference(duplicate, json_document=True))
        self.assertTrue(private_reference('{broken ' + private_values[0], json_document=True))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'docs').mkdir()
            (root / 'docs/lesson.json').write_text(public, encoding='utf-8')
            with patch('cs_study_map.validate.subprocess.run', return_value=SimpleNamespace(stdout=b'docs/lesson.json\0')), patch('cs_study_map.validate.read_jsonl', return_value=[]):
                self.assertEqual(audit_tracked(root), 1)
