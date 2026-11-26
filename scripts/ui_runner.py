"""Whitelisted local runner for the four educational fuzz targets.

No user-controlled commands or paths. The UI may use only run_experiment.py
and deterministic_checks.py within the project. Execution is synchronous.
"""
from __future__ import annotations
import json
import os
import platform
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / 'run_history'
ALLOWED_RUNS = (1000, 5000, 10000)
ALLOWED_SEEDS = (1, 7, 42)


def _linux_path(path: Path) -> str:
    absolute = path.resolve()
    drive = absolute.drive.rstrip(':').lower()
    if not drive or len(drive) != 1 or not str(absolute).startswith(absolute.drive + '\\'):
        raise ValueError('Expected project on a Windows local drive for WSL path mapping')
    return '/mnt/' + drive + absolute.as_posix()[2:]


def _command(n: int | None, mode: str, runs: int, seed: int) -> tuple[list[str], dict[str, str]]:
    if mode not in ('quick', 'fuzz'):
        raise ValueError('Unknown run mode')
    if mode == 'fuzz' and n not in (1, 2, 3, 4):
        raise ValueError('Unknown experiment')
    if runs not in ALLOWED_RUNS or seed not in ALLOWED_SEEDS:
        raise ValueError('Unsupported execution limits')
    relative = 'scripts/deterministic_checks.py' if mode == 'quick' else f'experiment_{n}/run_experiment.py'
    env = os.environ.copy()
    env.update(FUZZ_RUNS=str(runs), FUZZ_SEED=str(seed))
    if os.name == 'nt' and mode == 'fuzz':
        if not shutil.which('wsl.exe'):
            raise RuntimeError('WSL is missing. Run the application from Ubuntu or install WSL.')
        # The driver must use Python and Clang installed INSIDE WSL, not Windows Python.
        project = _linux_path(ROOT)
        return ['wsl.exe', '--cd', project, '--', 'env', f'FUZZ_RUNS={runs}', f'FUZZ_SEED={seed}',
                'python3', relative], env
    return [sys.executable, str(ROOT / relative)], env


def run_experiment(n: int | None, mode: str, runs: int = 1000, seed: int = 1) -> dict:
    """Run exactly one recognized script; snapshot its recorded evidence."""
    command, env = _command(n, mode, runs, seed)
    HISTORY.mkdir(exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6]
    folder = HISTORY / run_id
    folder.mkdir()
    started = datetime.now(timezone.utc).isoformat()
    timeout = 300 if mode == 'fuzz' else 45
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                text=True, errors='replace', timeout=timeout, check=False)
        exit_code = result.returncode
        output = (result.stdout or '') + ('\n' if result.stderr else '') + (result.stderr or '')
        error = None
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        output = (exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or '')
        error = f'Process exceeded the {timeout}-second limit'
    except (OSError, ValueError) as exc:
        exit_code = None
        output = ''
        error = str(exc)
    finished = datetime.now(timezone.utc).isoformat()
    (folder / 'runner_output.log').write_text(output[-200000:], encoding='utf-8')
    evidence = None
    if mode == 'fuzz' and n is not None and exit_code is not None:
        source = ROOT / f'Eksperimenti {n}.json'
        if source.exists():
            try:
                parsed = json.loads(source.read_text(encoding='utf-8'))
                # Only snapshots created during the current run are accepted.
                timestamp = parsed.get('timestamp_utc')
                if parsed.get('experiment') == n and timestamp and timestamp >= started:
                    evidence = parsed
                    shutil.copy2(source, folder / 'result.json')
            except (ValueError, OSError, TypeError):
                pass
    record = dict(id=run_id, mode=mode, experiment=n, runs=runs if mode == 'fuzz' else None,
                  seed=seed if mode == 'fuzz' else None, started_utc=started, finished_utc=finished,
                  exit_code=exit_code, success=(exit_code == 0), error=error,
                  evidence_status=evidence.get('status') if evidence else None,
                  source='WSL / Ubuntu' if os.name == 'nt' and mode == 'fuzz' else platform.system(),
                  log=f'run_history/{run_id}/runner_output.log',
                  snapshot=f'run_history/{run_id}/result.json' if evidence else None)
    (folder / 'run.json').write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding='utf-8')
    return record


def get_history(n: int | None = None) -> list[dict]:
    if not HISTORY.is_dir():
        return []
    rows = []
    for p in HISTORY.glob('*/run.json'):
        try:
            row = json.loads(p.read_text(encoding='utf-8'))
            if n is None or row.get('experiment') == n:
                rows.append(row)
        except (OSError, ValueError):
            continue
    return sorted(rows, key=lambda r: r.get('started_utc', ''), reverse=True)


def snapshot(record: dict) -> dict | None:
    relative = record.get('snapshot')
    if not isinstance(relative, str):
        return None
    file = (ROOT / relative).resolve()
    if not file.is_relative_to(HISTORY.resolve()) or not file.is_file():
        return None
    try:
        return json.loads(file.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
