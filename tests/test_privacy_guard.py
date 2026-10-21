import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


GUARD = Path(__file__).resolve().parents[1] / 'scripts' / 'privacy_guard.py'


class GitPrivacyGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.env['GIT_CONFIG_NOSYSTEM'] = '1'
        self.env['GIT_CONFIG_GLOBAL'] = os.devnull
        self.run_git('init', '-q')
        self.run_git('config', 'user.name', 'Test')
        self.run_git('config', 'user.email', '123+test@users.noreply.github.com')
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/privacy_guard.py').write_bytes(GUARD.read_bytes())
        self.guard('install', success=True)

    def run_git(self, *args, success=True):
        result = subprocess.run(['git', *args], cwd=self.root, env=self.env, capture_output=True)
        self.assertEqual(result.returncode == 0, success, 'Unexpected Git result (output withheld).')
        return result

    def guard(self, *args, success):
        result = subprocess.run([sys.executable, str(GUARD), *args], cwd=self.root, env=self.env, capture_output=True)
        self.assertEqual(result.returncode == 0, success, 'Unexpected privacy guard result.')
        return result

    def stage(self, text):
        (self.root / 'README.md').write_text(text, encoding='utf-8')
        self.run_git('add', 'README.md')

    def test_hooks_reject_staged_content_and_message(self):
        private = 'student' + '@' + 'private.invalid'
        self.stage(private)
        (self.root / 'README.md').write_text('clean working copy', encoding='utf-8')
        result = self.run_git('commit', '-qm', 'safe message', success=False)
        self.assertNotIn(private.encode(), result.stderr)
        self.stage('clean')
        self.run_git('commit', '-qm', 'Notes at ' + 'Q:' + '/private/notes', success=False)
        self.run_git('commit', '-qm', 'Add notes')

    def test_identity_override_and_encoded_path_blocked(self):
        self.stage('clean')
        self.env['GIT_AUTHOR_EMAIL'] = 'student' + '@' + 'private.invalid'
        self.run_git('commit', '-qm', 'Add notes', success=False)
        del self.env['GIT_AUTHOR_EMAIL']
        self.stage('Q%3A' + '%2Fprivate%2Fnotes')
        self.run_git('commit', '-qm', 'Add notes', success=False)

    def test_push_blocks_bad_ancestor_even_after_content_fixed(self):
        remote = self.root / 'remote.git'
        self.run_git('init', '--bare', '-q', str(remote))
        self.run_git('remote', 'add', 'origin', str(remote))
        self.stage('Q:' + '/private/notes')
        self.run_git('-c', 'core.hooksPath=', 'commit', '-qm', 'Bad ancestor')
        self.stage('clean')
        self.run_git('commit', '-qm', 'Clean current file')
        self.guard('index', success=True)
        self.run_git('push', 'origin', 'HEAD:main', success=False)

    def test_clean_commit_and_push_pass(self):
        remote = self.root / 'remote.git'
        self.run_git('init', '--bare', '-q', str(remote))
        self.run_git('remote', 'add', 'origin', str(remote))
        self.stage('docs/guide.md and https://github.com/example/project')
        self.run_git('commit', '-qm', 'Add public guide')
        self.run_git('push', 'origin', 'HEAD:main')

    def test_json_programs_pass_but_private_keys_and_values_still_fail(self):
        code = '\n'.join(['n = 2', 'while n:', '    n = n - 1'])
        path = self.root / 'lesson.json'
        path.write_text(json.dumps({'code': code}), encoding='utf-8')
        self.run_git('add', 'lesson.json')
        self.run_git('commit', '-qm', 'Add original program')
        private = 'Q:' + chr(92) + 'notes'
        for value in (json.dumps({'nested': [private]}), json.dumps({private: 'safe'}),
                      '{"key": ' + json.dumps(private) + ', "key": "safe"}'):
            path.write_text(value, encoding='utf-8')
            self.run_git('add', 'lesson.json')
            self.guard('index', success=False)
