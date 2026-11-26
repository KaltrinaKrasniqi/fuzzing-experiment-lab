"""Local libFuzzer runner with real replay and JSON provenance."""
import json, os, platform, re, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
ROOT=Path(__file__).resolve().parent.parent
N=int(sys.argv[1]);assert N in (3,4)
HERE=ROOT/f'experiment_{N}'
SOURCE=HERE/('message_parser.cpp' if N==3 else 'resource_cleanup.cpp')
TOKEN='heap-buffer-overflow' if N==3 else 'detected memory leaks'
RUNS=int(os.getenv('FUZZ_RUNS','10000'))
SEED=int(os.getenv('FUZZ_SEED','1'))

def rel(p):return p.relative_to(ROOT).as_posix()
def run(cmd,log,folder,env):
    start=perf_counter()
    with log.open('w',encoding='utf-8') as out:
        p=subprocess.run([str(x) for x in cmd],cwd=folder,stdout=out,stderr=subprocess.STDOUT,env=env,timeout=120)
    return p.returncode,round(perf_counter()-start,6),log.read_text(errors='replace')

def main():
    compiler=os.environ.get('CXX','clang++')
    try: compiler_version=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    except (OSError,subprocess.CalledProcessError):print('clang++ is required (use Ubuntu/WSL)');return 2
    d=Path(tempfile.mkdtemp(prefix='run-',dir=HERE))
    env=os.environ.copy()
    env['ASAN_OPTIONS']='detect_leaks=1:halt_on_error=1'
    env['LSAN_OPTIONS']='exitcode=23'
    binaries={}; builds={}
    for variant in ('buggy','fixed'):
        exe=d/f'fuzz-{variant}';log=d/f'build-{variant}.log'
        flags=['-std=c++17','-O1','-g','-fno-omit-frame-pointer','-fsanitize=fuzzer,address,leak']
        if variant=='fixed':flags.append('-DFIXED')
        code,_,_=run([compiler,*flags,SOURCE,'-o',exe],log,d,env)
        if code:print('Build failed:',log);return 2
        binaries[variant]=exe;builds[variant]=rel(log)
    rows=[]
    for variant in ('buggy','fixed'):
        log=d/f'libfuzzer-{variant}.log';artifact=d/f'crash-{variant}.bin'
        # Reproducible corpus seeds for structured formats, same initial corpus for both versions.
        corpus=d/f'corpus-{variant}';corpus.mkdir(exist_ok=True)
        # Benign seed is retained, triggering seed is NOT supplied to fuzzing.
        (corpus/'valid-seed').write_bytes(b'\xa5\x08'+b'\x01'*10 if N==3 else b'\xb4\x60')
        cmd=[binaries[variant],f'-runs={RUNS}',f'-seed={SEED}', '-max_len=32', '-print_final_stats=1',f'-exact_artifact_path={artifact}',corpus]
        code,duration,text=run(cmd,log,d,env)
        matches=re.search(r'stat::number_of_executed_units:\s*(\d+)',text)
        if not matches: matches=re.search(r'Done\s+(\d+)\s+runs',text)
        rows.append({'version':variant,'runs':int(matches.group(1)) if matches else None,'duration_seconds':duration,'exit_code':code,'log':rel(log),'artifact':rel(artifact) if artifact.exists() else None,'status':'Unverified'})
    artifact=d/'crash-buggy.bin';rlog=d/'replay.log'
    replayed=False;fixed_ok=False;inp=None
    if artifact.exists():
        inp=artifact.read_bytes()
        lines=[f'Input hex: {inp.hex()}']
        for variant in ('buggy','fixed'):
            cmd=[binaries[variant],'-runs=1',artifact]
            code,_,out=run(cmd,d/f'replay-{variant}.log',d,env)
            failed=TOKEN in out
            ok=code!=0 and failed if variant=='buggy' else code==0 and not failed
            lines.append(f'{variant}: exit={code}, sanitizer_detected={failed}, replay_verified={ok}')
            if variant=='buggy':replayed=ok
            else:fixed_ok=ok
        rlog.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    else:rlog.write_text('No crash artifact produced by this fuzzing run.\n',encoding='utf-8')
    fuzzfixed=rows[1]['exit_code']==0 and rows[1]['runs']==RUNS
    verified=replayed and fixed_ok and fuzzfixed
    rows[0]['status']='Error reproduced' if replayed else 'Not reproduced'
    rows[1]['status']='Fuzz run completed without reported errors' if fuzzfixed else 'Not verified'
    result={'experiment':N,'title':'Binary message parser' if N==3 else 'Resource cleanup on error','language':'C++','tool':'libFuzzer','detection_mechanism':'AddressSanitizer' if N==3 else 'LeakSanitizer','reported_error':TOKEN,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),'compiler':compiler_version,'seed':SEED,'run_limit_per_version':RUNS,'results':rows,'replay_log':rel(rlog),'replay':{'input_hex':inp.hex() if inp is not None else None},'build_logs':builds,'reproduced':replayed,'fixed_replay_ok':fixed_ok,'status':'Verifikuar' if verified else 'I paverifikuar','source_file':rel(SOURCE)}
    (ROOT/f'Eksperimenti {N}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Experiment {N}: {result["status"]}; {rlog}')
    return 0 if verified else 1
if __name__=='__main__':raise SystemExit(main())
