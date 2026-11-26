from pathlib import Path
import subprocess,sys
raise SystemExit(subprocess.call([sys.executable,str(Path(__file__).resolve().parent.parent/'scripts'/'run_cpp_fuzz.py'),'4']))
