import os, sys, json, traceback

# Ensure repo root (workspace/) is importable when running from scripts/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

print("PYTHON_VERSION:", sys.version)
print("CWD:", os.getcwd())
print("PYTHONPATH_HEAD:", sys.path[0])

try:
    from agents._lib.context_pg import fetch_context, learn
    print("IMPORT_OK: agents._lib.context_pg")
except Exception as e:
    print("IMPORT_FAIL:", repr(e))
    traceback.print_exc()
    sys.exit(1)

Q = os.environ.get("QUERY", "NovaOS")
print("QUERY:", Q)

try:
    results = fetch_context(Q, k=5)
    print("RESULT_COUNT:", len(results))
    if results:
        top = results[0]["content"]
        print("TOP_SNIPPET:", (top[:200] + ("..." if len(top) > 200 else "")).replace("\n"," "))
    ack = learn("smoketest", f"Smoketest for query: {Q}", tags=["smoke","ci"])
    print("LEARN_STATUS:", json.dumps(ack))
except Exception as e:
    print("SMOKE_FAIL:", repr(e))
    traceback.print_exc()
    sys.exit(1)
