#!/usr/bin/env python3
"""Nis eksperimentin e zgjedhur C++ me sanitizer-in perkates."""
import argparse
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="Ekzekutimi i eksperimentit C++")
parser.add_argument("--experiment", type=int, choices=(3, 4), required=True)
args = parser.parse_args()
script = root / f"experiment_{args.experiment}" / "run_experiment.py"
raise SystemExit(subprocess.call([sys.executable, str(script)]))
