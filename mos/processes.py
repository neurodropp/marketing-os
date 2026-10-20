"""Process contracts, pinned local work orders and evidence-backed completion records.

This module never executes an LLM or external action. Evidence truth is reviewed by
operators; hashes provide change detection, not authentication.
"""
from pathlib import Path
import hashlib
import json
from . import core as c


def hashed(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_hash(root, path):
    p = c.safe(root, path)
    c.require(p.is_file() and p.stat().st_size > 0, f"Missing or empty evidence file: {path}")
    return hashlib.sha256(p.read_bytes()).hexdigest()


def catalog(root=c.ROOT):
    reg = c.read(c.safe(root, 'registry.json'))
    data = c.read(c.safe(root, reg.get('process_catalog', 'catalog/processes.json')))
    c.require(data.get('schema_version') == '1.0', 'Unsupported process catalog schema')
    return data


def validate_catalog(root, reg, taxonomy):
    data = catalog(root)
    c.require(data['release'] == reg['release'], 'Process catalog release mismatch')
    expected = {p['id']: (d, p) for d in taxonomy['domains'] for p in d['processes']}
    skills = {s['id']: s for s in reg['skills']}
    seen = set()
    for p in data['processes']:
        pid = p['id']
        c.require(pid in expected and pid not in seen, 'Unknown or duplicate operational process')
        seen.add(pid)
        d, original = expected[pid]
        s = skills[d['skill']]
        c.require((p['domain'], p['skill'], p['agent'], p['name']) ==
                  (d['id'], s['id'], s['agent'], original['name']), 'Process ownership/name mismatch')
        c.require(p['version'] == s['version'], 'Process/skill version mismatch')
        c.require(p['path'] in s['references'], 'SOP is not discoverable through its skill')
        c.require(p['path'] == f"skills/{s['id']}/references/processes/{pid}.md", 'Invalid SOP path')
        c.require(c.safe(root, p['path']).is_file(), 'Missing SOP')
        c.require([step['capability'] for step in p['steps']] == [v['id'] for v in original['capabilities']],
                  'Process steps do not cover the exact ordered capability IDs')
        for key, prefix, text in [('inputs', 'i', 'description'), ('steps', 's', 'instruction'), ('quality_checks', 'q', 'criterion')]:
            items = p[key]
            c.require(items and [x['id'] for x in items] == [f'{prefix}{i+1}' for i in range(len(items))],
                      f'Invalid {key} IDs')
            c.require(all(isinstance(x[text], str) and x[text].strip() for x in items), f'Empty {key}')
        for key in ('trigger', 'output_contract', 'stop_condition', 'output_folder'):
            c.require(isinstance(p[key], str) and p[key].strip(), f'Missing process {key}')
        c.safe(root, p['output_folder'])
        c.require(p['handoff']['agent'] in {a['id'] for a in reg['agents']}, 'Unknown downstream agent')
    c.require(seen == set(expected), 'Every taxonomy process must have an operational SOP')
    return {p['id']: p for p in data['processes']}


def show(process_id, root=c.ROOT):
    matches = [p for p in catalog(root)['processes'] if p['id'] == process_id]
    c.require(len(matches) == 1, 'Unknown process ID')
    p = matches[0]
    return {**p, 'input_template': {i['id']: {'status': 'unknown', 'references': [], 'note': 'Describe the gap'} for i in p['inputs']}}


def memory_snapshot(project):
    return {i: hashed(r) for i, r in c.active_records(project).items() if r['status'] == 'approved'}


def validate_inputs(project, spec, inputs):
    c.require(isinstance(inputs, dict) and set(inputs) == {i['id'] for i in spec['inputs']}, 'Bind every input ID exactly once')
    pins = {}
    for item in inputs.values():
        c.require(isinstance(item, dict) and set(item) == {'status', 'references', 'note'}, 'Invalid input binding')
        c.require(item['status'] in {'provided', 'unknown', 'not-applicable'}, 'Invalid input status')
        c.require(isinstance(item['note'], str) and item['note'].strip(), 'Input explanation required')
        c.require(isinstance(item['references'], list) and all(isinstance(r, str) and r.strip() for r in item['references']), 'Invalid input references')
        if item['status'] == 'provided':
            c.require(item['references'], 'Provided input needs a source file')
        for path in item['references']:
            # Remote sources must be captured in a local source note with URL/date.
            pins[path] = file_hash(project, path)
    return pins


def start(project, process_id, run_id, objective, payload, root=c.ROOT):
    c.identifier(run_id)
    c.require(isinstance(objective, str) and objective.strip(), 'Objective required')
    c.validate_repo(root)
    spec = show(process_id, root)
    cfg = c.project_config(project)
    c.require(isinstance(payload, dict) and set(payload) == {'project_id', 'inputs'} and payload['project_id'] == cfg['project_id'], 'Input scope mismatch')
    reg = c.read(c.safe(root, 'registry.json'))
    agent = next(a for a in reg['agents'] if a['id'] == spec['agent'])
    skill = next(s for s in reg['skills'] if s['id'] == spec['skill'])
    paths = [agent['path'], skill['path'], spec['path'], f"skills/{skill['id']}/references/processes.md",
             'protocols/orchestration.md', 'protocols/contracts.md', 'protocols/second-brain.md', 'protocols/process-execution.md']
    with c.locked(project):
        pins = validate_inputs(project, spec, payload['inputs'])
        run = {'schema_version': '1.0', 'kind': 'process', 'project_id': cfg['project_id'], 'id': run_id,
               'process_id': process_id, 'objective': objective, 'created_at': c.now(), 'status': 'in-progress',
               'definition_hash': hashed(spec), 'pinned_files': {p: file_hash(root, p) for p in paths},
               'input_files': pins, 'inputs': payload['inputs'], 'approved_memory_snapshot': memory_snapshot(project),
               'onboarding_snapshot': intake_snapshot(project),
               'events': [{'at': c.now(), 'status': 'started'}]}
        c.save(c.safe(project, f'runs/process-{run_id}.json'), run, create=True)
    return {**run, 'sop_path': str(c.safe(root, spec['path'])), 'output_contract': spec['output_contract'],
            'completion_template': completion_template(run, spec)}


def intake_snapshot(project):
    p = c.safe(project, 'onboarding/state.json')
    if not p.exists():
        return None
    # Intake content matters; purely administrative history does not.
    from . import onboarding
    state = onboarding.load(project)
    return hashed({'answers': state['answers'], 'confirmation': state['confirmation']})


def completion_template(run, spec):
    return {'project_id': run['project_id'], 'run_id': run['id'], 'process_id': spec['id'],
            'status': 'draft', 'execution_mode': 'role-pass', 'artifacts': [],
            'review': {'reviewer': '', 'mode': 'role-pass', 'summary': ''},
            'checks': [{'id': q['id'], 'verdict': 'unverified', 'evidence': [], 'note': ''} for q in spec['quality_checks']],
            'actions': [], 'limitations': [], 'memory_proposals': [], 'next_action': ''}


def load_run(project, run_id):
    c.identifier(run_id)
    cfg = c.project_config(project)
    run = c.read(c.safe(project, f'runs/process-{run_id}.json'))
    c.require(run.get('schema_version') == '1.0' and run.get('kind') == 'process', 'Unsupported process run')
    c.require(run['project_id'] == cfg['project_id'] and run['id'] == run_id, 'Cross-project run refused')
    return run


def verify_context(project, run, root):
    c.require(run['definition_hash'] == hashed(show(run['process_id'], root)), 'Process definition changed; create a replacement run')
    c.require(run['approved_memory_snapshot'] == memory_snapshot(project), 'Approved memory changed; reconcile and replace run')
    c.require(run['onboarding_snapshot'] == intake_snapshot(project), 'Intake changed; reconcile and replace run')
    for path, value in run['pinned_files'].items():
        c.require(file_hash(root, path) == value, f'Pinned definition changed: {path}')
    for path, value in run['input_files'].items():
        c.require(file_hash(project, path) == value, f'Input evidence changed: {path}')


def finish(project, run_id, payload, root=c.ROOT):
    with c.locked(project):
        run = load_run(project, run_id)
        c.require(run['status'] == 'in-progress', 'Run already resolved; create a replacement run for revision')
        verify_context(project, run, root)
        spec = show(run['process_id'], root)
        template = completion_template(run, spec)
        c.require(isinstance(payload, dict) and set(payload) == set(template), 'Completion payload fields differ from template')
        c.require(all(payload[k] == template[k] for k in ('project_id', 'run_id', 'process_id')), 'Completion scope mismatch')
        c.require(payload['status'] in {'draft', 'ready', 'executed'}, 'Invalid completion status')
        c.require(payload['execution_mode'] in {'role-pass', 'delegated'}, 'Invalid execution mode')
        cfg = c.project_config(project)
        review = payload['review']
        c.require(isinstance(review, dict) and set(review) == {'reviewer', 'mode', 'summary'}, 'Review fields required')
        c.require(review['mode'] in {'role-pass', 'delegated'}, 'Invalid review mode')
        for k in ('reviewer', 'summary'):
            c.require(isinstance(review[k], str) and review[k].strip(), f'Review {k} required')
        if 'delegated' in (payload['execution_mode'], review['mode']):
            c.require(cfg['capabilities']['subagents'], 'Project does not declare delegation capability')
        files = {}
        def evidence(paths, required=False):
            c.require(isinstance(paths, list) and all(isinstance(p, str) and p.strip() for p in paths), 'Evidence paths must be an array of strings')
            c.require(not required or bool(paths), 'Local evidence file required')
            for p in paths:
                files[p] = file_hash(project, p)
        evidence(payload['artifacts'], required=True)
        # Deliverables must be in the selected process's working folder, not merely an input file or run JSON.
        for path in payload['artifacts']:
            c.require(Path(path).parts[0] == spec['output_folder'], 'Artifact must be in the process output folder')
        checks = payload['checks']
        c.require(isinstance(checks, list) and len(checks) == len(spec['quality_checks']) and
                  {q.get('id') for q in checks if isinstance(q, dict)} == {q['id'] for q in spec['quality_checks']}, 'Every quality gate must be reported exactly once')
        for q in checks:
            c.require(set(q) == {'id', 'verdict', 'evidence', 'note'}, 'Invalid quality gate fields')
            c.require(q['verdict'] in {'pass', 'fail', 'unverified'}, 'Invalid gate verdict')
            c.require(isinstance(q['note'], str) and q['note'].strip(), 'Gate explanation required')
            evidence(q['evidence'], required=q['verdict'] == 'pass')
        if payload['status'] != 'draft':
            c.require(all(q['verdict'] == 'pass' for q in checks), 'Ready/executed requires every gate to pass')
            c.require(all(i['status'] != 'unknown' for i in run['inputs'].values()), 'Unknown required inputs prevent ready/executed')
        for key in ('limitations', 'memory_proposals'):
            c.require(isinstance(payload[key], list) and all(isinstance(x, str) and x.strip() for x in payload[key]), f'{key} must be a string array')
        c.require(isinstance(payload['next_action'], str) and payload['next_action'].strip(), 'Next action or explicit completion note required')
        c.require(isinstance(payload['actions'], list), 'Action receipts must be an array')
        if payload['status'] == 'executed':
            c.require(payload['actions'], 'Executed status needs an observed external action receipt')
        for action in payload['actions']:
            c.require(isinstance(action, dict) and set(action) == {'target', 'effect', 'authorization', 'observed_result', 'evidence'}, 'Invalid action receipt')
            for key in ('target', 'effect', 'authorization', 'observed_result'):
                c.require(isinstance(action[key], str) and action[key].strip(), f'Action {key} required')
            evidence(action['evidence'], required=True)
        run['status'] = payload['status']
        run['completion'] = payload
        run['artifact_files'] = files
        run['events'].append({'at': c.now(), 'status': payload['status'], 'completion': payload})
        c.save(c.safe(project, f'runs/process-{run_id}.json'), run)
    return run


def status(project, run_id, root=c.ROOT):
    run = load_run(project, run_id)
    verify_context(project, run, root)
    for path, value in run.get('artifact_files', {}).items():
        c.require(file_hash(project, path) == value, f'Completed artifact/evidence changed: {path}')
    return run
