import json
import shutil
from pathlib import Path
import pytest
from automation.state import validate_repository_state
from automation.authorizations import validate_governance_authorization
from automation.history import load_quest_record_history


def test_retirement_passes_full_validation_and_history_cannot_authorize(tmp_path):
    for folder in ('automation','quests','calendar','memory','outputs','docs'):
        if Path(folder).exists():
            shutil.copytree(folder,tmp_path/folder)
    shutil.copy('AGENTS.md',tmp_path/'AGENTS.md')
    # Receipt paths can include implementation/tests outside the compact copy.
    for folder in ('src','tests','experiments','configs','scripts','.github'):
        if Path(folder).exists(): shutil.copytree(folder,tmp_path/folder)
    assert validate_repository_state(tmp_path)['valid']
    record=json.loads((tmp_path/'automation/authorizations/2026/09/AUTH-20260902T190916629850Z-arci-september-refine-b1c2d3e4f5a60718293a.json').read_text())
    with pytest.raises(ValueError,match='already-active'):
        validate_governance_authorization(record,delegations={},active_ids={'QST-SIM-0003'})
    history=load_quest_record_history(tmp_path)
    path=next(iter(history))
    (tmp_path/path).write_text((tmp_path/path).read_text()+'\n')
    with pytest.raises(ValueError,match='identity changed'):
        load_quest_record_history(tmp_path)
