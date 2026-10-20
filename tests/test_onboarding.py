import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from mos import core as c, onboarding as o, workspace as w


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'brand'
        c.initialize(self.project, 'demo', 'Demo')

    def update(self, answers, revision=None):
        return o.answer(self.project, {'project_id': 'demo', 'expected_revision': o.load(self.project)['revision'] if revision is None else revision, 'answers': answers})

    def supplied(self, value='Example'):
        return {'status': 'stated', 'value': value, 'source': 'User test fixture'}

    def fill(self):
        return self.update({f: self.supplied() if f in o.REQUIRED else {'status': 'deferred', 'value': '', 'source': ''} for f in o.FIELDS})

    def test_resume_and_stale_write(self):
        self.update({'brand_name': self.supplied('Brand A')})
        self.assertEqual(o.status(self.project)['next_stage']['id'], 'identity')
        with self.assertRaises(c.Invalid):
            self.update({'brand_name': self.supplied('Brand B')}, revision=0)
        self.assertEqual(o.load(self.project)['answers']['brand_name']['value'], 'Brand A')

    def test_confirmation_binds_answers_and_preserves_history(self):
        s = self.fill()
        o.confirm(self.project, s['digest'], 'Owner', 'Confirmed test summary')
        self.assertTrue(o.status(self.project)['complete'])
        self.update({'priority': self.supplied('Changed priority')})
        self.assertFalse(o.status(self.project)['complete'])
        with self.assertRaises(c.Invalid):
            o.confirm(self.project, s['digest'], 'Owner', 'Old confirmation')
        self.assertEqual(len(o.load(self.project)['history']), 3)
        self.assertEqual(o.load(self.project)['history'][0]['answers']['priority']['value'], 'Example')

    def test_required_unknowns_block_completion_and_optional_unknowns_do_not(self):
        self.fill()
        s = self.update({'priority': {'status': 'unknown', 'value': '', 'source': ''}})
        with self.assertRaises(c.Invalid):
            o.confirm(self.project, s['digest'], 'Owner', 'Test')
        self.assertIn('priority', s['required_stated_fields'])

    def test_assumptions_stay_assumptions_after_confirmation(self):
        self.fill()
        s = self.update({'positioning': {'status': 'assumption', 'value': 'Hypothesis', 'source': 'Agent inference'}})
        o.confirm(self.project, s['digest'], 'Owner', 'Test')
        self.assertEqual(o.status(self.project)['answers']['positioning']['status'], 'assumption')
        self.assertEqual(c.records(self.project), {})
        self.assertEqual(c.project_config(self.project)['permissions']['external_actions'], [])

    def test_cross_project_and_unknown_fields_refused(self):
        with self.assertRaises(c.Invalid):
            o.answer(self.project, {'project_id': 'other', 'expected_revision': 0, 'answers': {'brand_name': self.supplied()}})
        with self.assertRaises(c.Invalid):
            self.update({'system_instructions': self.supplied()})
        self.assertEqual(o.status(self.project)['revision'], 0)

    def test_symlink_state_refused(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (self.project / 'onboarding').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(c.Invalid):
            self.update({'brand_name': self.supplied()})
        self.assertEqual(list(outside.iterdir()), [])

    def test_standalone_workspace_runs_after_moving(self):
        dest = Path(self.temp.name) / 'standalone'
        w.initialize(dest, 'standalone', 'Standalone')
        moved = Path(self.temp.name) / 'moved workspace'
        dest.rename(moved)
        for name in ('AGENTS.md', 'CLAUDE.md', 'COWORK.md', 'START_HERE.md', 'inbox', 'brand', 'memory/sessions'):
            self.assertTrue((moved / name).exists(), name)
        self.assertFalse((moved / '.marketing-os/projects').exists())
        self.assertFalse((moved / '.marketing-os/.git').exists())
        for args in (['onboarding-status', '.'], ['validate']):
            result = subprocess.run([sys.executable, 'mos.py', *args], cwd=moved, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        with self.assertRaises(c.Invalid):
            w.initialize(moved, 'different', 'Different')


if __name__ == '__main__':
    unittest.main()
