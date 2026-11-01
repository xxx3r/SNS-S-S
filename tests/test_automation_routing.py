import json
import subprocess
from pathlib import Path

import pytest

from automation.routing_guard import receipt_result_ref, validate_routing_transition
from automation.standing import validate_standing_request


@pytest.fixture
def routing_tree(tmp_path):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(tmp_path), *args], text=True).strip()
    git('init', '-q')
    git('config', 'user.name', 'Fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    active = tmp_path / 'quests/active'
    active.mkdir(parents=True)
    (active / 'README.md').write_text(
        '# Active\n1. [QST-SIM-0003: Power](QST-SIM-0003-power.md)\n\nNext: telemetry\n'
    )
    (active / 'QST-SIM-0003-power.md').write_text(
        '# QST-SIM-0003: Power\nStatus: Active\nPriority: P1\n\nNext: telemetry\n'
    )
    (tmp_path / 'quests/research_graph.json').write_text(json.dumps({
        'nodes': [{'id': 'QST-SIM-0003', 'status': 'active', 'priority': 'P1'}], 'edges': [],
    }))
    git('add', '.')
    git('commit', '-qm', 'Accepted quest state')
    source = git('rev-parse', 'HEAD')
    request = {
        'loop_id': 'weekly-evidence-synthesis', 'action': 'route', 'scope': 'research-tooling',
        'acceptance_slice': 'Reconcile accepted direction without lifecycle changes',
        'paths': ['quests/active/README.md', 'quests/active/QST-SIM-0003-power.md', 'quests/research_graph.json'],
        'budgets': {'worlds': 0, 'records': 0, 'runtime_s': 0, 'disk_mb': 1},
        'transaction_count': 1, 'evidence_refs': ['Accepted telemetry'],
        'routing_source_commit': source,
    }
    return tmp_path, source, request, git


def validate(tree):
    root, source, request, _ = tree
    policy = json.loads(Path('automation/standing/2026-10.v1.json').read_text())
    validate_standing_request(policy, request, now='2026-10-18T06:00:00Z',
                              source_root=root, source_commit=source)


def test_existing_quest_and_index_routing_prose_can_change(routing_tree):
    root, _, _, _ = routing_tree
    for path in (root / 'quests/active').glob('*.md'):
        path.write_text(path.read_text().replace('Next: telemetry', 'Next: delivery attribution'))
    validate(routing_tree)


@pytest.mark.parametrize('operation', ['add', 'remove'])
def test_coordinated_membership_edit_cannot_borrow_route_authority(routing_tree, operation):
    root, _, _, _ = routing_tree
    index = root / 'quests/active/README.md'
    graph = root / 'quests/research_graph.json'
    data = json.loads(graph.read_text())
    if operation == 'add':
        (root / 'quests/active/QST-NEW-0001.md').write_text('# QST-NEW-0001\nStatus: Active\n')
        index.write_text(index.read_text() + '\n2. [QST-NEW-0001: New](QST-NEW-0001.md)\n')
        data['nodes'].append({'id': 'QST-NEW-0001', 'status': 'active', 'priority': 'P1'})
    else:
        (root / 'quests/active/QST-SIM-0003-power.md').unlink()
        index.write_text('# No active quests\n')
        data['nodes'] = []
    graph.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='file membership'):
        validate(routing_tree)


@pytest.mark.parametrize('before,after', [
    ('Status: Active', 'Status: Completed'), ('Priority: P1', 'Priority: P0'),
    ('# QST-SIM-0003: Power', '# QST-NEW-0001: New'),
])
def test_route_freezes_existing_quest_identity_status_and_priority(routing_tree, before, after):
    root, _, _, _ = routing_tree
    path = root / 'quests/active/QST-SIM-0003-power.md'
    path.write_text(path.read_text().replace(before, after))
    with pytest.raises(ValueError, match='identity/status/priority'):
        validate(routing_tree)


def test_route_cannot_change_index_membership_alone(routing_tree):
    root, _, _, _ = routing_tree
    path = root / 'quests/active/README.md'
    path.write_text(path.read_text().replace('QST-SIM-0003', 'QST-NEW-0001'))
    with pytest.raises(ValueError, match='index membership'):
        validate(routing_tree)


def test_route_cannot_change_graph_structure_or_metadata(routing_tree):
    root, _, _, _ = routing_tree
    path = root / 'quests/research_graph.json'
    data = json.loads(path.read_text())
    data['nodes'][0]['priority'] = 'P0'
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='graph data'):
        validate(routing_tree)


def test_route_requires_source_binding_and_existing_target(routing_tree):
    root, source, request, _ = routing_tree
    request.pop('routing_source_commit')
    with pytest.raises(ValueError, match='receipt source'):
        validate(routing_tree)
    request['routing_source_commit'] = '0' * 40
    with pytest.raises(ValueError, match='receipt source'):
        validate(routing_tree)
    request['routing_source_commit'] = source
    request['paths'].append('quests/active/new-registry.txt')
    (root / 'quests/active/new-registry.txt').write_text('new registration')
    with pytest.raises(ValueError, match='Git evidence'):
        validate(routing_tree)


def test_historical_replay_uses_receipt_introduction_not_future_queue(routing_tree):
    root, source, request, git = routing_tree
    path = root / 'quests/active/QST-SIM-0003-power.md'
    path.write_text(path.read_text().replace('Next: telemetry', 'Next: delivery attribution'))
    receipt = Path('automation/runs/2026/10/routing-witness.json')
    (root / receipt).parent.mkdir(parents=True)
    (root / receipt).write_text(json.dumps({'request': request}))
    assert receipt_result_ref(root, receipt) is None
    validate(routing_tree)
    git('add', '.')
    git('commit', '-qm', 'Accepted routing reconciliation and immutable receipt')
    introduced = git('rev-parse', 'HEAD')
    path.unlink()
    git('add', '.')
    git('commit', '-qm', 'Later separately authorized lifecycle transition')
    assert receipt_result_ref(root, receipt) == introduced
    validate_routing_transition(root, source, request['paths'], result_ref=introduced)
    with pytest.raises(ValueError, match='file membership'):
        validate(routing_tree)


def test_receipt_store_enforces_transition_and_replays_accepted_tree(routing_tree):
    from automation.ids import new_run_id
    from automation.provenance import build_state_snapshot, build_run_receipt_v2
    from automation.receipts import ReceiptStore, validate_run_receipt

    root, _, request, git = routing_tree
    records = {
        'stable_law': 'AGENTS.md',
        'active_contract': 'automation/contracts/weekly-evidence-synthesis.v2.md',
        'state_ownership': 'automation/state_ownership.json',
        'active_quest_index': 'quests/active/README.md',
        'research_graph': 'quests/research_graph.json',
        'runtime_manifest': 'automation/runtime_manifest.json',
        'canonical_memory': 'memory/mem_log_short.md',
        'standing_pointer': 'automation/standing/current.json',
        'standing_authority': 'automation/standing/2026-10.v1.json',
    }
    for path in records.values():
        target = root / path
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(Path(path).read_bytes())
    # Historical October fixture must bind the October pointer explicitly;
    # the live November pointer is not part of the fixture's accepted source.
    (root / records['standing_pointer']).write_text(
        json.dumps({'path': records['standing_authority']}) + '\n'
    )
    git('add', '.')
    git('commit', '-qm', 'Accepted policy and source records')
    source = git('rev-parse', 'HEAD')
    request['routing_source_commit'] = source
    snapshot = build_state_snapshot(root, source_commit=source, records=records)
    path = root / 'quests/active/QST-SIM-0003-power.md'
    path.write_text(path.read_text().replace('Next: telemetry', 'Next: delivery attribution'))
    policy_text = (root / records['standing_authority']).read_text()
    policy = json.loads(policy_text)
    receipt = build_run_receipt_v2({
        'run_id': new_run_id('weekly-evidence-synthesis'),
        'loop_id': 'weekly-evidence-synthesis', 'contract_version': '2.0.0',
        'trigger': 'explicit-human', 'trigger_time': '2026-10-18T06:00:00Z',
        'created_at': '2026-10-18T06:00:01Z', 'source_commit': source,
        'quest_context': {}, 'pr_context': {}, 'consumed_ids': [],
        'artifacts': ['quests/active/QST-SIM-0003-power.md'], 'belief_effects': [],
        'checks': [{'name': name, 'status': 'passed', 'evidence': 'Synthetic fixture check'}
                   for name in policy['required_checks']],
        'terminal_state': 'DONE', 'next_action': 'Continue accepted routing',
        'decision_effect': 'Preserve membership while reconciling fixture prose',
        'observability': {'continuity': 'independent'},
        'standing_execution': {'policy_json': policy_text, 'requests': [request],
                              'trigger_id': 'weekly-evidence-synthesis:2026-10-18T06:00:00+00:00'},
    }, state_snapshot=snapshot)
    store = ReceiptStore(root / 'automation/runs')
    store.write(receipt)
    git('add', '.')
    git('commit', '-qm', 'Accepted routing receipt')
    path.unlink()
    git('add', '.')
    git('commit', '-qm', 'Later separately authorized lifecycle work')
    assert store.load_all()[0]['run_id'] == receipt['run_id']
    # A fresh receipt cannot reuse the older source to hide today's deletion.
    receipt['run_id'] = new_run_id('weekly-evidence-synthesis')
    with pytest.raises(ValueError, match='file membership'):
        validate_run_receipt(receipt, source_root=root)
