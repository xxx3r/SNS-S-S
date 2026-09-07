"""Bounded standing authority: validate actions without a per-slice permission hop.

This validates structural authority, not the truth of evidence or review quality.
Live source, scope interpretation, reviewers and checks remain mandatory gates.
"""
from __future__ import annotations

from datetime import datetime, timezone
from fnmatch import fnmatchcase
from pathlib import PurePosixPath
from typing import Mapping

ROLE_ACTIONS = {
    'daily-governance-triage': {'maintenance', 'merge', 'route'},
    'daily-research-operator': {'implement', 'merge'},
    'weekly-evidence-synthesis': {'implement', 'maintenance', 'merge', 'activate', 'terminalize', 'route'},
    'monthly-governance': {'govern', 'literature', 'merge'},
}
BUDGET_CEILINGS = {'worlds':64, 'records':100000, 'runtime_s':600, 'disk_mb':100}
CAPS = {'daily-governance-triage': 2, 'daily-research-operator': 1,
        'weekly-evidence-synthesis': 4, 'monthly-governance': 1}
ACTION_SURFACES = {
    'implement': ('src/**', 'experiments/**', 'configs/**', 'tests/**', 'outputs/**', 'docs/**', 'automation/runs/**', 'automation/pr_lifecycle/**'),
    'maintenance': ('tests/**', 'docs/**', 'scripts/**', 'automation/runs/**', 'automation/pr_lifecycle/**'),
    'activate': ('quests/**', 'memory/**', 'automation/quest_history/**', 'automation/runs/**', 'automation/pr_lifecycle/**'),
    'terminalize': ('quests/**', 'memory/**', 'automation/quest_history/**', 'automation/runs/**', 'automation/pr_lifecycle/**'),
    'route': ('memory/**', 'automation/runs/**', 'automation/pr_lifecycle/**'),
    'literature': ('calendar/evidence/**', 'calendar/belief_events/**', 'calendar/roundups/**', 'automation/runs/**'),
}
PROTECTED = ('AGENTS.md', 'AURORA.md', 'automation/contracts/**', 'automation/schemas/**',
             'automation/standing.py', 'automation/state.py', 'automation/receipts.py',
             'automation/state_ownership.json', 'automation/orchestration.py',
             'automation/prompts/**', 'automation/runtime_manifest.json', '.github/**')


def instant(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('authority timestamps require timezone')
    return result.astimezone(timezone.utc)


def safe_path(value: str) -> str:
    if not isinstance(value, str) or not value or '\\' in value or any(c in value for c in '*?['):
        raise ValueError('requested paths must be concrete repository paths')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value:
        raise ValueError('requested paths must be canonical relative paths')
    return value


def validate_standing_policy(policy: Mapping[str, object]) -> None:
    required = {'schema', 'policy_id', 'authority', 'recorded_at', 'expires_at', 'review_at',
                'research_scopes', 'roles', 'budget_caps', 'required_checks'}
    if required - set(policy) or policy.get('schema') != 'sns.standing-authority.v1':
        raise ValueError('invalid standing authority schema or missing fields')
    if policy['authority'] not in {'explicit-human', 'monthly-governance'}:
        raise ValueError('standing authority must be human or Monthly owned')
    if not str(policy['policy_id']).startswith('STAND-'):
        raise ValueError('invalid standing policy ID')
    if not instant(policy['recorded_at']) < instant(policy['review_at']) <= instant(policy['expires_at']):
        raise ValueError('invalid standing authority validity/review interval')
    if not policy['research_scopes'] or not policy['required_checks']:
        raise ValueError('standing authority requires research scopes and checks')
    if set(policy['roles']) != set(ROLE_ACTIONS):
        raise ValueError('standing authority must specify all four action roles')
    for role, row in policy['roles'].items():
        if not set(row['actions']) <= ROLE_ACTIONS[role] or not row['actions']:
            raise ValueError('role cannot widen its constitutional action set')
        if type(row['max_transactions']) is not int or not 1 <= row['max_transactions'] <= CAPS[role]:
            raise ValueError('role transaction cap exceeded')
        if not row['write_surfaces']:
            raise ValueError('role requires explicit write surfaces')
    caps = policy['budget_caps']
    if set(caps) != {'worlds', 'records', 'runtime_s', 'disk_mb'}:
        raise ValueError('standing budget dimensions are fixed')
    if any(type(v) is not int or not 0 < v <= BUDGET_CEILINGS[k] for k, v in caps.items()):
        raise ValueError('budget caps must stay inside constitutional ceilings')


def validate_standing_request(policy: Mapping[str, object], request: Mapping[str, object], *, now: str) -> None:
    validate_standing_policy(policy)
    required = {'loop_id', 'action', 'scope', 'acceptance_slice', 'paths', 'budgets',
                'transaction_count', 'evidence_refs'}
    if required - set(request):
        raise ValueError('standing request missing fields')
    if not instant(policy['recorded_at']) <= instant(now) < instant(policy['expires_at']):
        raise ValueError('standing authority is not current')
    role = request['loop_id']
    if role not in policy['roles']:
        raise ValueError('unknown standing role')
    rules = policy['roles'][role]
    action = request['action']
    if action not in rules['actions']:
        raise ValueError('action outside role authority')
    if request['scope'] not in policy['research_scopes'] or not str(request['acceptance_slice']).strip():
        raise ValueError('action requires a bounded approved research scope')
    count = request['transaction_count']
    if type(count) is not int or not 1 <= count <= rules['max_transactions']:
        raise ValueError('transaction budget exceeded')
    if not isinstance(request['paths'], list) or not request['paths']:
        raise ValueError('effectful action requires a non-empty concrete paths list')
    for item in request['paths']:
        path = safe_path(item)
        if any(fnmatchcase(path, pattern) for pattern in PROTECTED):
            raise ValueError('protected authority surface requires human transaction')
        if action in ACTION_SURFACES and not any(fnmatchcase(path, pattern) for pattern in ACTION_SURFACES[action]):
            raise ValueError('write outside action surfaces')
        if not any(fnmatchcase(path, pattern) for pattern in rules['write_surfaces']):
            raise ValueError('write outside role surfaces')
        # Tests of authority and their helpers are control-plane law, not routine maintenance.
        if action != 'govern' and (path.startswith('automation/') and not path.startswith(('automation/runs/', 'automation/pr_lifecycle/', 'automation/quest_history/')) or path.startswith('tests/test_automation_')):
            raise ValueError('control-plane changes require a dedicated human transaction')
    budgets = request['budgets']
    if not isinstance(budgets, dict) or set(budgets) != set(policy['budget_caps']):
        raise ValueError('request must declare all budget dimensions')
    for name, amount in budgets.items():
        if type(amount) is not int or not 0 <= amount <= policy['budget_caps'][name]:
            raise ValueError('experiment budget outside standing cap')
    if not isinstance(request['evidence_refs'], list):
        raise ValueError('evidence_refs must be a list')
    if action in {'activate', 'terminalize', 'merge'} and not request['evidence_refs']:
        raise ValueError('lifecycle action requires accepted evidence or reviewed proposal references')
    if any(not isinstance(ref, str) or not ref.strip() for ref in request['evidence_refs']):
        raise ValueError('empty evidence reference')
