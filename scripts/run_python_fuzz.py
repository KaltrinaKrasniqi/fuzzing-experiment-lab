"""Atheris runner. Run from Python with Atheris installed, preferably Linux/WSL."""
import json, os, re, subprocess, sys, tempfile, platform
from importlib.metadata import version
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
ROOT=Path(__file__).resolve().parent.parent
N= int(sys.argv[1])
assert N in (1,2)
HERE=ROOT/f'experiment_{N}'
SCRIPT= HERE/('fuzz_order.py' if N==1 else 'fuzz_loyalty.py')
RUNS=int(os.getenv('FUZZ_RUNS','10000'))
SEED=int(os.getenv('FUZZ_SEED','1'))

def rel(path):return path.relative_to(ROOT).as_posix()
def run(command, log, cwd):
    t=perf_counter()
    with log.open('w',encoding='utf-8') as f:
        proc=subprocess.run([str(x) for x in command],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
    return proc.returncode,round(perf_counter()-t,6),log.read_text(errors='replace')

def main():
    try: av=version('atheris')
    except Exception as e: print('Atheris is required: python3 -m pip install atheris');return 2
    rundir=Path(tempfile.mkdtemp(prefix='run-',dir=HERE))
    corpus=HERE/'seed_corpus'
    rows=[]
    for variant in ('buggy','fixed'):
        log=rundir/f'atheris-{variant}.log'; artifact=rundir/f'crash-{variant}.bin'
        cmd=[sys.executable,SCRIPT,variant,f'-runs={RUNS}',f'-seed={SEED}', '-max_len=256',f'-exact_artifact_path={artifact}','-print_final_stats=1',corpus]
        code,duration,text=run(cmd,log,rundir)
        match=re.search(r'stat::number_of_executed_units:\s*(\d+)',text)
        if not match: match=re.search(r'Done\s+(\d+)\s+runs',text)
        rows.append({'version':variant,'runs':int(match.group(1)) if match else None,'duration_seconds':duration,'exit_code':code,'log':rel(log),'artifact':rel(artifact) if artifact.exists() else None, 'status':'Unverified'})
    artifact=rundir/'crash-buggy.bin'; replaylog=rundir/'replay.log'
    replayed=False; fixed_replay_ok=False; details={}
    if artifact.exists():
        data=artifact.read_bytes()
        if N==1:
            sys.path.insert(0,str(HERE));from order_parser import parse_order,OrderValidationError
            try:parse_order(data,False)
            except (TypeError,AttributeError,KeyError,OverflowError,ZeroDivisionError) as exc:
                replayed=True;details['exception']=repr(exc)
            try:parse_order(data,True);fixed_replay_ok=True
            except OrderValidationError:fixed_replay_ok=True
            except Exception:fixed_replay_ok=False
        else:
            sys.path.insert(0,str(HERE));from loyalty_rules import test_order,OracleMismatch
            try:test_order(data,False)
            except OracleMismatch as exc:replayed=True;details['exception']=str(exc)
            try:test_order(data,True);fixed_replay_ok=True
            except Exception:fixed_replay_ok=False
        details['input_hex']=data.hex();details['input_utf8']=data.decode('utf-8','replace')
    replaylog.write_text(json.dumps({'reproduced':replayed,'fixed_replay_ok':fixed_replay_ok,**details},ensure_ascii=False,indent=2),encoding='utf-8')
    passed=(rows[0]['exit_code']!=0 and replayed and fixed_replay_ok and rows[1]['exit_code']==0 and rows[1]['runs']==RUNS)
    rows[0]['status']='Error reproduced' if replayed else 'Not reproduced'
    rows[1]['status']='Fuzz run completed without reported errors' if rows[1]['exit_code']==0 and rows[1]['runs']==RUNS else 'Not verified'
    result={'experiment':N,'title':'Order JSON parser' if N==1 else 'Loyalty and discount rules','language':'Python','tool':'Atheris','detection_mechanism':'Unexpected exception' if N==1 else 'Reference oracle','reported_error':'TypeError' if N==1 else 'OracleMismatch','timestamp_utc':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),'python_version':platform.python_version(),'atheris_version':av,'run_limit_per_version':RUNS,'seed':SEED,'results':rows,'replay_log':rel(replaylog),'replay':details,'reproduced':replayed,'fixed_replay_ok':fixed_replay_ok,'status':'Verifikuar' if passed else 'I paverifikuar','source_file':rel(HERE/('order_parser.py' if N==1 else 'loyalty_rules.py'))}
    (ROOT/f'Eksperimenti {N}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Experiment {N}: {result["status"]}; {replaylog}')
    return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
