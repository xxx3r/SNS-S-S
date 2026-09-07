import copy
import json
from pathlib import Path
import pytest
from automation.standing import validate_standing_policy, validate_standing_request


def policy():
    return json.loads(Path('automation/standing/2026-09.v1.json').read_text())


def request(role='daily-research-operator', action='implement'):
    return {'loop_id':role, 'action':action, 'scope':'thermal-storage',
            'acceptance_slice':'Tiny development fixture', 'paths':['experiments/thermal.py'],
            'budgets':{'worlds':3,'records':30,'runtime_s':10,'disk_mb':1},
            'transaction_count':1,'evidence_refs':[]}


def test_daily_can_work_without_triage_authorization():
    validate_standing_request(policy(), request(), now='2026-09-07T12:00:00Z')


@pytest.mark.parametrize('change', [
    {'paths':[]}, {'paths':['../AGENTS.md']}, {'paths':['AGENTS.md']},
    {'paths':['automation/contracts/daily.v2.md']},
    {'paths':['tests/test_automation_standing_authority.py']},
    {'paths':['quests/active/README.md']}, {'scope':'unapproved architecture'},
    {'transaction_count':2}, {'action':'activate'},
    {'budgets':{'worlds':65,'records':30,'runtime_s':10,'disk_mb':1}},
])
def test_daily_cannot_widen_authority(change):
    r=request();r.update(change)
    with pytest.raises(ValueError):
        validate_standing_request(policy(), r, now='2026-09-07T12:00:00Z')


def test_expiry_and_weekly_lifecycle_evidence():
    with pytest.raises(ValueError,match='not current'):
        validate_standing_request(policy(), request(), now='2026-10-01T06:00:00Z')
    r=request('weekly-evidence-synthesis','terminalize')
    r['paths']=['quests/active/README.md','quests/completed/QST-SYNTH-0001.md']
    with pytest.raises(ValueError,match='requires accepted evidence'):
        validate_standing_request(policy(), r, now='2026-09-07T12:00:00Z')
    r['evidence_refs']=['outputs/accepted-comparison.json']
    r['transaction_count']=4
    validate_standing_request(policy(), r, now='2026-09-07T12:00:00Z')
    r['transaction_count']=5
    with pytest.raises(ValueError,match='budget exceeded'):
        validate_standing_request(policy(), r, now='2026-09-07T12:00:00Z')


def test_triage_can_merge_reviewed_science_but_cannot_implement_it():
    r=request('daily-governance-triage','merge');r['evidence_refs']=['PR qualified head']
    validate_standing_request(policy(),r,now='2026-09-07T12:00:00Z')
    r['action']='maintenance';r['paths']=['src/sim/thermal.py']
    with pytest.raises(ValueError,match='action surfaces'):
        validate_standing_request(policy(),r,now='2026-09-07T12:00:00Z')
    p=copy.deepcopy(policy());p['roles']['daily-governance-triage']['actions'].append('govern')
    with pytest.raises(ValueError,match='constitutional'):
        validate_standing_policy(p)


def test_policy_cannot_raise_constitutional_budget_ceiling():
    p=policy();p['budget_caps']['worlds']=1000000
    with pytest.raises(ValueError,match='constitutional ceilings'):
        validate_standing_policy(p)


@pytest.fixture
def action_receipt(tmp_path):
    import subprocess
    from automation.provenance import snapshot_fingerprint, git_blob_sha
    def git(*args):
        return subprocess.check_output(['git','-C',str(tmp_path),*args],text=True).strip()
    git('init','-q');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
    target=tmp_path/'automation/standing';target.mkdir(parents=True)
    for name in ['current.json','2026-09.v1.json']:
        (target/name).write_bytes(Path('automation/standing',name).read_bytes())
    git('add','.');git('commit','-qm','Accepted policy fixture')
    receipt=json.loads(next(Path('automation/runs/2026/09').glob('*system-audit*.json')).read_text())
    receipt['observability']={'continuity':'independent'}
    receipt['decision_effect']='Fixture implementation only'
    receipt['receipt_kind']='run';receipt.pop('correction_of',None)
    receipt['consumed_ids']=[];receipt['belief_effects']=[];receipt['artifacts']=['experiments/thermal.py']
    receipt['checks']=[{'name':name,'status':'passed','evidence':'Fixture qualification result'} for name in policy()['required_checks']]
    receipt['loop_id']='daily-research-operator';receipt['contract_version']='2.0.0'
    receipt['created_at']='2026-09-07T12:00:00Z';receipt['trigger_time']='2026-09-07T11:00:00Z'
    receipt['source_commit']=git('rev-parse','HEAD')
    receipt['state_snapshot']['source_commit']=receipt['source_commit']
    receipt['state_snapshot']['records'] += [{'role':role,'path':f'automation/standing/{name}','git_blob_sha':git_blob_sha((target/name).read_bytes())} for role,name in [('standing_pointer','current.json'),('standing_authority','2026-09.v1.json')]]
    receipt['state_snapshot']['fingerprint']=snapshot_fingerprint(receipt['state_snapshot'])
    receipt['standing_execution']={'policy_json':(target/'2026-09.v1.json').read_text(),'requests':[request()], 'trigger_id':'daily-research-operator:2026-09-07T11:00:00+00:00'}
    return receipt,tmp_path


def test_action_receipt_binds_exact_policy_bytes(action_receipt):
    from automation.receipts import validate_run_receipt
    from automation.provenance import snapshot_fingerprint,git_blob_sha
    receipt,root=action_receipt
    validate_run_receipt(receipt,source_root=root)
    receipt['standing_execution']['policy_json']+='\n'
    with pytest.raises(ValueError,match='do not match source snapshot'):
        validate_run_receipt(receipt,source_root=root)
    # Updating the self-declared identity too must still fail against Git source.
    receipt['state_snapshot']['records'][-1]['git_blob_sha']=git_blob_sha(receipt['standing_execution']['policy_json'].encode())
    receipt['state_snapshot']['fingerprint']=snapshot_fingerprint(receipt['state_snapshot'])
    with pytest.raises(ValueError,match='differs from accepted source'):
        validate_run_receipt(receipt,source_root=root)


def test_empty_requests_require_no_effects(action_receipt):
    from automation.receipts import validate_run_receipt
    r,root=action_receipt;r['standing_execution']['requests']=[]
    with pytest.raises(ValueError,match='empty standing requests'):
        validate_run_receipt(r,source_root=root)
    r.update(artifacts=[],belief_effects=[],consumed_ids=[],decision_effect='NO_ACTION')
    validate_run_receipt(r,source_root=root)


def test_trigger_id_cannot_be_reset_in_receipt(action_receipt):
    from automation.receipts import validate_run_receipt
    r,root=action_receipt;r['standing_execution']['trigger_id']='reset'
    with pytest.raises(ValueError,match='trigger_id'):
        validate_run_receipt(r,source_root=root)


def test_trigger_accounting_across_receipt_files(action_receipt):
    from automation.receipts import ReceiptStore
    r,root=action_receipt
    store=ReceiptStore(root/'automation/runs');store.write(r)
    other=copy.deepcopy(r)
    from automation.ids import new_run_id
    other['run_id']=new_run_id('daily-research-operator')
    other['standing_execution']['requests'][0]['acceptance_slice']='Another slice'
    with pytest.raises(ValueError,match='reuse transaction indices'):
        store.write(other)


def test_weekly_budget_cannot_be_split_across_receipts(action_receipt):
    from automation.receipts import ReceiptStore
    from automation.ids import new_run_id
    r,root=action_receipt;r['loop_id']='weekly-evidence-synthesis'
    r['standing_execution']['trigger_id']='weekly-evidence-synthesis:2026-09-07T11:00:00+00:00'
    req=r['standing_execution']['requests'][0];req['loop_id']=r['loop_id'];req['budgets']['worlds']=40
    store=ReceiptStore(root/'automation/runs');store.write(r)
    other=copy.deepcopy(r);other['run_id']=new_run_id(r['loop_id'])
    req=other['standing_execution']['requests'][0];req['acceptance_slice']='Second slice';req['transaction_count']=2
    with pytest.raises(ValueError,match='aggregate standing budget'):
        store.write(other)
    req['budgets']['worlds']=24;store.write(other)
    # Loading externally deposited files enforces the same aggregate rule.
    path=next(p for p in (root/'automation/runs').glob('**/*.json') if other['run_id'] in p.name)
    req['budgets']['worlds']=25;path.write_text(json.dumps(other))
    with pytest.raises(ValueError,match='aggregate standing budget'):
        store.load_all()


def test_standing_receipt_and_runtime_match_normative_schemas(action_receipt):
    from jsonschema import Draft202012Validator
    r,_=action_receipt
    for data,schema_path in [(r,'automation/schemas/loop-run-v2.schema.json'), (json.loads(Path('automation/runtime_manifest.json').read_text()),'automation/schemas/runtime-manifest.schema.json')]:
        schema=json.loads(Path(schema_path).read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(data)


def test_standing_effects_require_policy_checks(action_receipt):
    from automation.receipts import validate_run_receipt
    r,root=action_receipt;r['checks']=[]
    with pytest.raises(ValueError,match='all required checks'):
        validate_run_receipt(r,source_root=root)
    r['checks']=[{'name':name,'status':'not_run','evidence':'Not executed'} for name in policy()['required_checks']]
    r['terminal_state']='DONE'
    with pytest.raises(ValueError,match='passed policy checks'):
        validate_run_receipt(r,source_root=root)
    r['terminal_state']='VERIFICATION_FAILED'
    validate_run_receipt(r,source_root=root)
