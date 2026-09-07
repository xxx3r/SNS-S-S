"""Read-only snapshot utility for the hosted provenance-snapshot workflow."""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import urllib.request
from pathlib import Path
from automation.contracts import _parse_frontmatter
from automation.ids import new_run_id
from automation.provenance import snapshot_from_connector_records


def snapshot_for_loop(root: Path, loop_id: str, source_commit: str, open_prs: list) -> dict:
    actual=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    if source_commit != actual:
        raise ValueError('snapshot source differs from checked-out accepted commit')
    def git(*args):
        return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
    paths=set(git('ls-tree','-r','--name-only',source_commit).splitlines())
    active=[]
    for path in sorted(paths):
        if path.startswith('automation/contracts/') and path.endswith('.md'):
            meta=_parse_frontmatter(git('show',f'{source_commit}:{path}'))
            if meta.get('loop_id')==loop_id and meta.get('status')=='active':active.append(path)
    if len(active)!=1:raise ValueError('source must have exactly one active loop contract')
    records={'stable_law':'AGENTS.md','active_contract':active[0],
             'state_ownership':'automation/state_ownership.json','active_quest_index':'quests/active/README.md',
             'research_graph':'quests/research_graph.json','runtime_manifest':'automation/runtime_manifest.json',
             'canonical_memory':'memory/mem_log_short.md'}
    pointer='automation/standing/current.json'
    if pointer in paths:
        records['standing_pointer']=pointer
        records['standing_authority']=json.loads(git('show',f'{source_commit}:{pointer}'))['path']
    monthly=sorted(p for p in paths if p.startswith('calendar/monthly/') and Path(p).stem[:4].isdigit())
    if monthly:records['monthly_state']=monthly[-1]
    rows=[{'role':role,'path':path,'git_blob_sha':git('rev-parse',f'{source_commit}:{path}')} for role,path in records.items()]
    return snapshot_from_connector_records(source_commit=source_commit,records=rows,open_prs=open_prs)



def api(path):
    request=urllib.request.Request('https://api.github.com/repos/xxx3r/SNS-S-S/'+path,
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--loop-id',required=True)
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args()
    if api('branches/main')['commit']['sha'] != args.source_commit:
        raise ValueError('accepted main moved; request a fresh snapshot')
    rows=[]
    for page in range(1,101):
        prs=api(f'pulls?state=open&per_page=100&page={page}')
        rows.extend({'number':p['number'],'head_sha':p['head']['sha'],'draft':p['draft'],'state':'open'} for p in prs)
        if len(prs)<100:break
    else:raise ValueError('open PR pagination incomplete')
    snapshot=snapshot_for_loop(Path.cwd(),args.loop_id,args.source_commit,rows)
    if api('branches/main')['commit']['sha'] != args.source_commit:
        raise ValueError('accepted main moved during snapshot')
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'snapshot.json').write_text(json.dumps(snapshot,indent=2,sort_keys=True)+'\n')
    ids={'run_id':new_run_id(args.loop_id),'note':'Generated identity only; no research run or receipt was executed.'}
    (out/'ids.json').write_text(json.dumps(ids,indent=2)+'\n')
    print(json.dumps({'snapshot':snapshot,'generated_ids':ids},sort_keys=True))

if __name__=='__main__':main()
