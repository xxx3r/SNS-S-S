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
    {'paths':['../AGENTS.md']}, {'paths':['AGENTS.md']},
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


def test_action_receipt_binds_exact_policy_bytes():
    from automation.receipts import validate_run_receipt
    from automation.provenance import snapshot_fingerprint,git_blob_sha
    receipt=json.loads(next(Path('automation/runs/2026/09').glob('*system-audit*.json')).read_text())
    receipt['loop_id']='daily-research-operator';receipt['contract_version']='2.0.0'
    receipt['created_at']='2026-09-07T12:00:00Z'
    ptext=Path('automation/standing/2026-09.v1.json').read_text()
    receipt['state_snapshot']['records'].append({'role':'standing_authority','path':'automation/standing/2026-09.v1.json','git_blob_sha':git_blob_sha(ptext.encode())})
    receipt['state_snapshot']['fingerprint']=snapshot_fingerprint(receipt['state_snapshot'])
    receipt['standing_execution']={'policy_json':ptext,'requests':[request()]}
    validate_run_receipt(receipt)
    receipt['standing_execution']['policy_json']=ptext+'\n'
    with pytest.raises(ValueError,match='do not match source snapshot'):
        validate_run_receipt(receipt)
