import json
import shutil
import subprocess
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
    source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    subprocess.run(['git','init',str(tmp_path)],check=True,capture_output=True)
    subprocess.run(['git','-C',str(tmp_path),'fetch',str(Path.cwd()),source],check=True,capture_output=True)
    subprocess.run(['git','-C',str(tmp_path),'update-ref','HEAD',source],check=True,capture_output=True)
    assert validate_repository_state(tmp_path)['valid']
    record=json.loads((tmp_path/'automation/authorizations/2026/09/AUTH-20260902T190916629850Z-arci-september-refine-b1c2d3e4f5a60718293a.json').read_text())
    with pytest.raises(ValueError,match='already-active'):
        validate_governance_authorization(record,delegations={},active_ids={'QST-SIM-0003'})
    history=load_quest_record_history(tmp_path)
    path=next(iter(history))
    (tmp_path/path).write_text((tmp_path/path).read_text()+'\n')
    with pytest.raises(ValueError,match='identity changed'):
        load_quest_record_history(tmp_path)


def test_archive_context_cannot_be_changed_with_matching_local_hash(tmp_path):
    # Use the actual source object database while isolating all mutable fixtures.
    shutil.copytree('automation',tmp_path/'automation')
    subprocess.run(['git','init',str(tmp_path)],check=True,capture_output=True)
    source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    subprocess.run(['git','-C',str(tmp_path),'fetch',str(Path.cwd()),source],check=True,capture_output=True)
    subprocess.run(['git','-C',str(tmp_path),'update-ref','HEAD',source],check=True,capture_output=True)
    shutil.copytree('quests',tmp_path/'quests')
    archive_path=tmp_path/'automation/quest_history/2026-09-06-pre-retirement.json'
    original=archive_path.read_text();archive=json.loads(original)
    archive['queues']['active'].append('QST-FAKE-0001')
    archive_path.write_text(json.dumps(archive))
    with pytest.raises(ValueError,match='queue context differs'):
        load_quest_record_history(tmp_path)
    archive_path.write_text(original)
    envelope=tmp_path/'automation/delegations/history/2026-09-arci.json'
    envelope.write_text(envelope.read_text()+'\n')
    with pytest.raises(ValueError,match='delegation bytes differ'):
        load_quest_record_history(tmp_path)
