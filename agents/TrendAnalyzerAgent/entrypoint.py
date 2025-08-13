import os, sys, time, runpy, requests
from pathlib import Path

AGENT_NAME = "TrendAnalyzer"
AGENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = AGENT_DIR.parent.parent  # .../src
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(AGENT_DIR)

try:
    target = AGENT_DIR / "main.py"
    if target.exists():
        runpy.run_path(str(target), run_name="__main__")
    else:
        # idle heartbeat; exit 0 so supervisor doesn't mark as error
        time.sleep(60)
        sys.exit(0)
except SystemExit as e:
    sys.exit(e.code if isinstance(e.code, int) else 0)
except Exception as e:
    print(f"[TrendAnalyzer entrypoint] error: {e}", flush=True)
    sys.exit(1)
