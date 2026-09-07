"""Replay immutable quest records against a previously qualified queue context.

Archives bind exact record bytes, not just IDs. New or changed records use live
validation. Archives are appended by reviewed lifecycle transactions from their
accepted source; they never authorize execution of historical records.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
from .provenance import git_blob_sha


def load_quest_record_history(root: str | Path) -> dict[str, dict]:
    repo = Path(root)
    result = {}
    for path in sorted((repo / 'automation/quest_history').glob('*.json')):
        archive = json.loads(path.read_text())
        if archive.get('schema') != 'sns.quest-record-history.v1':
            raise ValueError('invalid quest record history schema')
        source = archive.get('source_commit', '')
        if not re.fullmatch(r'[0-9a-f]{40}', source):
            raise ValueError('quest history requires accepted source identity')
        def git(*args):
            try:
                return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as exc:
                raise ValueError('historical source objects unavailable or not accepted ancestors; fetch full history') from exc
        git('merge-base', '--is-ancestor', source, 'HEAD')
        source_paths = git('ls-tree', '-r', '--name-only', source).decode().splitlines()
        source_queues = {name: set() for name in ('active', 'completed', 'proposed', 'blocked')}
        source_delegations = {}
        for source_path in source_paths:
            for queue in source_queues:
                if source_path.startswith(f'quests/{queue}/') and source_path.endswith('.md') and not source_path.endswith('README.md'):
                    match = re.search(r'QST-[A-Z0-9]+-[0-9]{4}', source_path)
                    if match: source_queues[queue].add(match.group())
            if source_path.startswith('automation/delegations/') and source_path.endswith('.json'):
                payload = git('show', f'{source}:{source_path}')
                envelope = json.loads(payload)
                source_delegations[envelope['delegation_id']] = payload

        context = archive['queues']
        if set(context) != {'active', 'completed', 'proposed', 'blocked'}:
            raise ValueError('invalid historical queue context')
        if {name: set(ids) for name, ids in context.items()} != source_queues:
            raise ValueError('historical queue context differs from declared source commit')
        for record in archive['records']:
            record_path = record['path']
            if not record_path.startswith(('automation/authorizations/', 'quests/actions/')) or '..' in Path(record_path).parts:
                raise ValueError('invalid historical record path')
            if record_path in result:
                raise ValueError('historical record already archived')
            source_blob = git('rev-parse', f'{source}:{record_path}').decode().strip()
            if source_blob != record['git_blob_sha']:
                raise ValueError('historical record hash differs from declared source commit')
            if not (repo / record_path).is_file() or git_blob_sha((repo / record_path).read_bytes()) != record['git_blob_sha']:
                raise ValueError('historical record identity changed or missing')
            data = json.loads((repo / record_path).read_text())
            if record_path.startswith('automation/authorizations/'):
                delegation_id = data['authorization']['delegation_id']
                expected = source_delegations.get(delegation_id)
                current = [p.read_bytes() for p in (repo / 'automation/delegations').glob('**/*.json')
                           if json.loads(p.read_text()).get('delegation_id') == delegation_id]
                if expected is None or current != [expected]:
                    raise ValueError('historical delegation bytes differ from declared source commit')
            result[record_path] = {name: set(ids) for name, ids in context.items()}
    return result
