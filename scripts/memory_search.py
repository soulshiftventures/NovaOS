import os, json
from agents._lib.context_pg import fetch_context, learn

Q = os.environ.get("QUERY", "NovaOS")
results = fetch_context(Q, k=5)
print("QUERY:", Q)
print("RESULT_COUNT:", len(results))
if results:
    print("TOP_SNIPPET:", results[0]["content"][:200].replace("\n"," ") + ("..." if len(results[0]["content"])>200 else ""))

# write a tiny event so we can confirm writes
ack = learn("smoketest", f"Smoketest for query: {Q}", tags=["smoke","ci"])
print("LEARN_STATUS:", json.dumps(ack))
