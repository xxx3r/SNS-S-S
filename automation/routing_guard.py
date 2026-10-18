"""Preserve accepted quest membership during a Weekly routing transaction."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ['git', '-C', str(root), *args], text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError('routing requires available source/result Git evidence') from exc


def validate_routing_transition(root, source_commit, paths, *, result_ref=None):
    """Check the actual proposed tree, or a receipt's immutable introduction tree.

    Index entries, active-file identities/metadata and graph data are frozen.
    Routing may reconcile prose in existing active documents; it may not create,
    delete, rename, activate, retire, reprioritize or change graph structure.
    """
    root = Path(root)
    if not isinstance(source_commit, str) or not re.fullmatch('[0-9a-f]{40}', source_commit):
        raise ValueError('quest routing requires routing_source_commit')
    _git(root, 'merge-base', '--is-ancestor', source_commit, result_ref or 'HEAD')

    def before(path):
        return _git(root, 'show', f'{source_commit}:{path}')

    def after(path):
        if result_ref:
            return _git(root, 'show', f'{result_ref}:{path}')
        target = root / path
        if not target.is_file():
            raise ValueError('routing cannot delete an accepted quest file')
        return target.read_text(encoding='utf-8')

    def active_files(ref):
        if ref:
            files = _git(root, 'ls-tree', '-r', '--name-only', ref, 'quests/active').splitlines()
            return sorted(p for p in files if Path(p).parent.as_posix() == 'quests/active' and p.endswith('.md'))
        return sorted(p.relative_to(root).as_posix() for p in (root / 'quests/active').glob('*.md'))

    source_files = active_files(source_commit)
    if source_files != active_files(result_ref):
        raise ValueError('routing cannot change active quest file membership')
    # Even nested/non-Markdown paths must already exist, preventing a path grant
    # for a future registry file that the membership parser might later consume.
    for path in paths:
        if path.startswith('quests/active/'):
            before(path)
            after(path)
    index_path = 'quests/active/README.md'
    index_entries = r'^\s*\d+\.\s+\[(QST-[A-Z0-9]+-[0-9]{4}):[^\n]*\]\(([^)]+)\)'
    if re.findall(index_entries, before(index_path), re.M) != re.findall(index_entries, after(index_path), re.M):
        raise ValueError('routing cannot change active index membership')
    metadata = r'^(?:# .+|Status:.*|Priority:.*|Tags:.*)$'
    for path in source_files:
        if path != index_path and re.findall(metadata, before(path), re.M) != re.findall(metadata, after(path), re.M):
            raise ValueError('routing cannot change quest identity/status/priority metadata')
    graph_path = 'quests/research_graph.json'
    if json.loads(before(graph_path)) != json.loads(after(graph_path)):
        raise ValueError('routing cannot change research graph data; use lifecycle/governance actions')


def receipt_result_ref(root, receipt_path):
    """Replay against the commit that first stored an immutable receipt.

    New uncommitted receipts use the current worktree. Later lifecycle changes
    must not invalidate an already accepted, unchanged routing receipt.
    """
    commits = _git(Path(root), 'log', '--reverse', '--format=%H', '--diff-filter=A', '--', str(receipt_path)).splitlines()
    return commits[0] if commits else None
