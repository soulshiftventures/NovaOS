import os, sys, time, runpy
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = AGENT_DIR.parent.parent  # .../src
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.chdir(AGENT_DIR)

try:
    runpy.run_path(str(AGENT_DIR / "main.py"), run_name="__main__")
except SystemExit as e:
    sys.exit(e.code if isinstance(e.code, int) else 1)
except Exception as e:
    print(f"[NovaCore entrypoint] error: {e}", flush=True)
    sys.exit(1)
