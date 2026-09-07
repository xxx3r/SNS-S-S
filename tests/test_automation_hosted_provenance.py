from pathlib import Path
import subprocess
import pytest
from scripts.provenance_snapshot import snapshot_for_loop
from automation.provenance import validate_state_snapshot


def test_hosted_snapshot_uses_real_source_and_current_role():
    root=Path.cwd();source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    snapshot=snapshot_for_loop(root,'daily-research-operator',source,[])
    validate_state_snapshot(snapshot)
    roles={row['role']:row['path'] for row in snapshot['records']}
    assert roles['active_contract'].startswith('automation/contracts/daily-research-operator.')
    for row in snapshot['records']:
        assert row['git_blob_sha']==subprocess.check_output(['git','rev-parse',source+':'+row['path']],text=True).strip()
    with pytest.raises(ValueError,match='source differs'):
        snapshot_for_loop(root,'daily-research-operator','0'*40,[])
