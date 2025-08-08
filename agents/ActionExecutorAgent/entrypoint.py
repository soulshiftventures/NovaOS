import os, sys, time, runpy
from pathlib import Path
AGENT_DIR = Path(__file__).resolve().parent
os.chdir(AGENT_DIR)
if __name__ == "__main__":
    try:
        runpy.run_path(str(AGENT_DIR / "main.py"), run_name="__main__")
    except SystemExit as e:
        sys.exit(e.code if isinstance(e.code, int) else 1)
    except Exception as e:
        print(f"[Executor entrypoint] error: {e}", flush=True)
        sys.exit(1)
