import copy
from pathlib import Path
import tempfile
import unittest
from mos import core as c, processes as p, onboarding as o


class ProcessExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'brand'
        c.initialize(self.project, 'demo', 'Demo')
        (self.project / 'source.md').write_text('Synthetic supplied evidence for state tests, not a real brand.')

    def start(self, pid='F1.03', rid='test', unknown=False):
        spec = p.show(pid)
        return p.start(self.project, pid, rid, 'Synthetic process contract test', {
            'project_id': 'demo', 'inputs': {i['id']: {'status': 'unknown' if unknown else 'provided',
            'references': [] if unknown else ['source.md'], 'note': 'Synthetic input'} for i in spec['inputs']}})

    def payload(self, run, state='ready'):
        spec = p.show(run['process_id'])
        out = self.project / spec['output_folder'] / run['id'] / 'result.md'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text('Synthetic artifact for contract validation; not a real marketing result.')
        result = copy.deepcopy(run['completion_template'])
        result.update(status=state, artifacts=[str(out.relative_to(self.project))], next_action='Fixture complete',
                      review={'reviewer':'Fixture reviewer','mode':'role-pass','summary':'Structural test only'})
        for q in result['checks']:
            q.update(verdict='pass', evidence=['source.md'], note='Synthetic gate declaration')
        return result

    def test_all_108_process_contracts_start_finish_and_resume(self):
        specs = p.catalog()['processes']
        self.assertEqual(len(specs), 108)
        for spec in specs:
            with self.subTest(process=spec['id']):
                rid = spec['id'].lower().replace('.', '-')
                run = self.start(spec['id'], rid)
                p.finish(self.project, rid, self.payload(run))
                self.assertEqual(p.status(self.project, rid)['status'], 'ready')

    def test_failed_or_missing_gate_cannot_be_ready(self):
        run = self.start()
        payload = self.payload(run)
        payload['checks'][0]['verdict'] = 'fail'
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload['checks'][0].update(verdict='pass', evidence=[])
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload['checks'] = payload['checks'][:-1]
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        self.assertEqual(p.status(self.project, 'test')['status'], 'in-progress')

    def test_unknown_inputs_allow_draft_but_not_readiness(self):
        run = self.start(unknown=True)
        payload = self.payload(run)
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload['status'] = 'draft'
        payload['checks'][0].update(verdict='unverified', evidence=[], note='No source available')
        payload['limitations'] = ['Required data unavailable']
        self.assertEqual(p.finish(self.project, 'test', payload)['status'], 'draft')

    def test_modified_input_blocks_completion(self):
        run = self.start()
        payload = self.payload(run)
        (self.project / 'source.md').write_text('Changed evidence')
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)

    def test_changed_approved_memory_blocks_completion(self):
        run = self.start()
        payload = self.payload(run)
        c.memory_add(self.project, {'id':'decision','kind':'decision','subject':'Scope','content':'Changed scope','evidence':['User fixture']})
        c.memory_accept(self.project, 'decision', 'Fixture', 'Synthetic approval')
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)

    def test_changed_intake_blocks_completion(self):
        run = self.start()
        payload = self.payload(run)
        o.answer(self.project, {'project_id':'demo','expected_revision':0,'answers':{
            'priority':{'status':'stated','value':'New priority','source':'User fixture'}}})
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)

    def test_executed_requires_receipts_and_authority_reference(self):
        run = self.start()
        payload = self.payload(run, 'executed')
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload['actions'] = [{'target':'synthetic account','effect':'synthetic action','authorization':'',
                              'observed_result':'Synthetic receipt','evidence':['source.md']}]
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload['actions'][0]['authorization'] = 'Explicit fixture authorization; not real action'
        self.assertEqual(p.finish(self.project, 'test', payload)['status'], 'executed')

    def test_artifact_mutation_detected_and_history_not_overwritten(self):
        run = self.start()
        payload = self.payload(run)
        p.finish(self.project, 'test', payload)
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        (self.project / payload['artifacts'][0]).write_text('Changed output')
        with self.assertRaises(c.Invalid): p.status(self.project, 'test')
        stored = c.read(self.project/'runs/process-test.json')
        self.assertEqual(len(stored['events']), 2)

    def test_cross_project_and_symlink_evidence_rejected(self):
        run = self.start()
        payload = self.payload(run)
        payload['project_id'] = 'other'
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload['project_id'] = 'demo'
        (self.project/'linked.md').symlink_to(self.project/'source.md')
        payload['checks'][0]['evidence'] = ['linked.md']
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload['checks'][0]['evidence'] = ['../outside.md']
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)

    def test_workflow_cannot_bypass_required_sop_runs(self):
        c.create_run(self.project, 'campaign-launch', 'campaign', 'Fixture campaign')
        h = {'project_id':'demo','step_id':'s1','execution_mode':'role-pass','deliverable':'Fixture',
             'sources':['source.md'],'assumptions':[],'acceptance':'Fixture','memory_proposals':[]}
        c.complete_step(self.project, 'campaign', 's1', h)
        h['step_id'] = 's2'
        with self.assertRaises(c.Invalid): c.complete_step(self.project, 'campaign', 's2', h)
        run = self.start('O1.04')
        p.finish(self.project, 'test', self.payload(run))
        h['process_runs'] = ['test']
        c.complete_step(self.project, 'campaign', 's2', h)
        (self.project/'source.md').write_text('Changed accepted source')
        h['step_id'] = 's3'
        with self.assertRaises(c.Invalid): c.complete_step(self.project, 'campaign', 's3', h)

    def test_duplicate_gate_and_delegation_declaration_rejected(self):
        run = self.start()
        payload = self.payload(run)
        payload['checks'][1] = copy.deepcopy(payload['checks'][0])
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload = self.payload(run)
        payload['review']['mode'] = 'delegated'
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)

    def test_empty_or_misplaced_artifact_rejected(self):
        run = self.start()
        payload = self.payload(run)
        payload['artifacts'] = ['source.md']
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)
        payload = self.payload(run)
        (self.project/payload['artifacts'][0]).write_text('')
        with self.assertRaises(c.Invalid): p.finish(self.project, 'test', payload)


if __name__ == '__main__': unittest.main()
