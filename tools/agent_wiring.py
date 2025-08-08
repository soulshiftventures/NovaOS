import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "agents"
DASH_DIR = ROOT / "services" / "novaos_dashboard"
ALLOWLIST = DASH_DIR / "agent_allowlist.txt"

def find_agents():
    if not AGENTS_DIR.exists():
        return []
    out = []
    for d in sorted(AGENTS_DIR.iterdir()):
        if d.is_dir() and (d / "main.py").exists():
            out.append(d.name)
    return out

ENTRYPOINT_TPL = """\
import os, sys, time, runpy, requests
from pathlib import Path

AGENT_NAME = "__AGENT_NAME__"
AGENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = AGENT_DIR.parent.parent  # repo root
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(AGENT_DIR)

MCP_MEMORY_URL = os.getenv("MCP_MEMORY_URL")

def mem_write(p):
    if not MCP_MEMORY_URL: 
        return
    try:
        requests.post(MCP_MEMORY_URL.rstrip('/') + "/tools/memory.write", json={"data": p}, timeout=5)
    except Exception:
        pass

mem_write({"agent": AGENT_NAME, "type":"event", "topic":"lifecycle", "payload":{"status":"starting"}, "ts": time.time()})

code = 0
try:
    runpy.run_path(str(AGENT_DIR / "main.py"), run_name="__main__")
except SystemExit as e:
    code = int(e.code) if isinstance(e.code, int) else 1
except Exception as e:
    print(f"[{AGENT_NAME} entrypoint] error: {e}", flush=True)
    code = 1

mem_write({"agent": AGENT_NAME, "type":"event", "topic":"lifecycle", "payload":{"status":"exited","code":code}, "ts": time.time()})
sys.exit(code)
"""

def ensure_entrypoints(agent_names):
    wrote = []
    for name in agent_names:
        ep = AGENTS_DIR / name / "entrypoint.py"
        if not ep.exists():
            ep.write_text(ENTRYPOINT_TPL.replace("__AGENT_NAME__", name))
            wrote.append(name)
    return wrote

def load_allowlist(all_agents):
    DASH_DIR.mkdir(parents=True, exist_ok=True)
    if ALLOWLIST.exists():
        allowed = [ln.strip() for ln in ALLOWLIST.read_text().splitlines()
                   if ln.strip() and not ln.strip().startswith("#")]
    else:
        # Default: safe subset on 512MB
        allowed = [a for a in all_agents if any(k in a.lower() for k in ["core","executor","fetcher","worker","scheduler"])]
        if not allowed:
            allowed = [a for a in all_agents if "perplexity" in a.lower()] or all_agents[:3]
        ALLOWLIST.write_text("\n".join(allowed) + "\n")
    return [a for a in allowed if a in all_agents]

def write_supervisor(allowed):
    conf = f"""[supervisord]
nodaemon=true
logfile=/dev/null
pidfile=/tmp/supervisord.pid
loglevel=info

[program:health]
command=/bin/bash -lc 'uvicorn health:app --host 0.0.0.0 --port ${{PORT:-8080}}'
directory=.
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
priority=10
stopasgroup=true
killasgroup=true
"""
    prio = 20
    for name in allowed:
        conf += f"""
[program:{name.lower()}]
command=/usr/bin/env python3 -u agents/{name}/entrypoint.py
directory=../..
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
stdout_logfile_maxbytes=0
stderr_logfile_maxbytes=0
priority={prio}
stopasgroup=true
killasgroup=true
"""
        prio += 5
    (DASH_DIR / "supervisord.conf").write_text(conf)

def ensure_packages():
(AGENTS_DIR / "__init__.py").touch()
    (AGENTS_DIR / "_lib" / "__init__.py").parent.mkdir(parents=True, exist_ok=True)
    (AGENTS_DIR / "_lib" / "__init__.py").touch()

def main():
    ensure_packages()
    agents = find_agents()
    if not agents:
        print("No agents with main.py found under ./agents")
        sys.exit(1)
    wrote = ensure_entrypoints(agents)
    allowed = load_allowlist(agents)
    write_supervisor(allowed)
    print("Agents found:", agents)
    print("EntryPoints created (new):", wrote)
    print("Allowed to run:", allowed)
    print("Wrote:", str(DASH_DIR / "supervisord.conf"), "and", str(ALLOWLIST))

if __name__ == "__main__":
    main()
