"""Replay immutable quest records against a previously qualified queue context.

Archives bind exact record bytes, not just IDs. New or changed records use live
validation. Archives are appended by reviewed lifecycle transactions from their
accepted source; they never authorize execution of historical records.
"""
from __future__ import annotations
import json
from pathlib import Path
from .provenance import git_blob_sha


def load_quest_record_history(root: str | Path) -> dict[str, dict]:
    repo = Path(root)
    result = {}
    for path in sorted((repo / 'automation/quest_history').glob('*.json')):
        archive = json.loads(path.read_text())
        if archive.get('schema') != 'sns.quest-record-history.v1':
            raise ValueError('invalid quest record history schema')
        if len(archive.get('source_commit', '')) != 40:
            raise ValueError('quest history requires accepted source identity')
        context = archive['queues']
        if set(context) != {'active', 'completed', 'proposed', 'blocked'}:
            raise ValueError('invalid historical queue context')
        for record in archive['records']:
            record_path = record['path']
            if not record_path.startswith(('automation/authorizations/', 'quests/actions/')) or '..' in Path(record_path).parts:
                raise ValueError('invalid historical record path')
            if record_path in result:
                raise ValueError('historical record already archived')
            if not (repo / record_path).is_file() or git_blob_sha((repo / record_path).read_bytes()) != record['git_blob_sha']:
                raise ValueError('historical record identity changed or missing')
            result[record_path] = {name: set(ids) for name, ids in context.items()}
    return result
