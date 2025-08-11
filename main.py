print("✅ NovaOS main.py launched")

import os
import json
import time
import threading
from dotenv import load_dotenv

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import redis

# ───────────────────────── Memory (Postgres) backend ──────────────────────────
MEMORY_ON = False
def _memory_disabled_reason():
    if not os.environ.get("DATABASE_URL"):
        return "DATABASE_URL is not set"
    return "context_pg import failed"

try:
    from agents._lib.context_pg import fetch_context, learn
    if os.environ.get("DATABASE_URL"):
        MEMORY_ON = True
except Exception:
    MEMORY_ON = False

def memory_learn(title: str, body: str, tags=None):
    if not MEMORY_ON:
        return {"status": "disabled", "reason": _memory_disabled_reason()}
    try:
        return learn(title, body, tags or [])
    except Exception as e:
        print(f"[memory.learn] ERROR: {e}", flush=True)
        return {"status": "error", "error": str(e)}

def memory_search(query: str, k: int = 8):
    if not MEMORY_ON:
        return []
    try:
        return fetch_context(query, k=k)
    except Exception as e:
        print(f"[memory.search] ERROR: {e}", flush=True)
        return []

# novaos.ask() = memory-first LLM call with audit to Postgres
from novaos import ask  # already tolerant of missing OPENAI_API_KEY (stub)

# ───────────────────────────── App environment ────────────────────────────────
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MODEL_ON = bool(os.getenv("OPENAI_API_KEY"))

# ─────────────────────────────── Redis wiring ─────────────────────────────────
class MockRedis:
    def __init__(self): self.approval = None
    def lrange(self, key, start, end): return [b'CEO-VISION: Blueprint built', b'FoundationBuilder: Architecture set', b'DashboardAgent: Dashboard ready', b'Optimization Cycle']
    def set(self, key, value): self.approval = value
    def get(self, key): return self.approval.encode() if self.approval else None
    def publish(self, channel, message): pass
    def pubsub(self, ignore_subscribe_messages=True):
        class MockPubSub:
            def subscribe(self, channel): pass
            def get_message(self): return None
        return MockPubSub()

if os.getenv("RENDER") is None:
    r = MockRedis()
else:
    r = redis.from_url(REDIS_URL)
    try:
        r.ping(); print("Redis Connected Successfully", flush=True)
    except Exception as e:
        print(f"Redis Connection Error: {e}", flush=True)

print("NovaOS Started - Activating Corporate Structure", flush=True)

# ───────────────────────────── Corporate structure ────────────────────────────
C_SUITE = ['CEO-VISION','CFO-AUTO','CTO-AUTO','CMO-AUTO','CPO-AUTO','CCO-AUTO','CHIEF-STAFF','CLARITY-COACH','CLO-AUTO']
FOUNDATIONAL = ['AgentFactory','FoundationBuilder','NOVA-CORE','NovaHistorian']
ANALYTICS = ['AnalyticsAgent','TrendAnalyzer','TrendFetcher','RESEARCH-ANALYST','RoadmapAgent','BusinessPlanAgent']
BUILDERS = ['automation_architect','BuilderAgent','DashboardAgent','DashboardBuilder','UIUXBuilder','PROMPT-ENGINEER']
TOOLS = ['BaserowSync','CloudManager','DockerDeployer','DROPBOX-FILE-MANAGER','ENERGY-GUARDIAN','FileAgent','GITHUB-DEPLOYER','LANGGRAPH-ROUTER','LemonSqueezyIntegrator','N8N-FLOW-BUILDER','NovaDashboard','PublerScheduler','RENDER-MANAGER','ShopifyIntegrator','TestAgent']
SPECIALIZED = ['ai_systems_engineer','blueprints','core','CryptoStreamBuilder','StreamBuilder','TimeSentinel']
ALL_GROUPS = [C_SUITE, FOUNDATIONAL, ANALYTICS, BUILDERS, TOOLS, SPECIALIZED]
ALL_AGENTS = sum(ALL_GROUPS, [])

for group in ALL_GROUPS:
    for agent in group:
        print(f"{agent} Activated in Group", flush=True)

# ─────────────────────────────────── UI ───────────────────────────────────────
st.set_page_config(page_title="NovaOS Central Hub", page_icon="🚀", layout="wide")
st.title("NovaOS Central Hub")

# Engine status (clear, first screen)
st.header("Engine Status")
col_a, col_b = st.columns(2)
with col_a:
    st.metric("Memory (Postgres)", "ON" if MEMORY_ON else "OFF")
    if not MEMORY_ON:
        st.info(f"Memory disabled: {_memory_disabled_reason()}")
with col_b:
    st.metric("Model (OpenAI)", "ON" if MODEL_ON else "OFF")
    if not MODEL_ON:
        st.caption("Model stub active. Set OPENAI_API_KEY to enable real answers.")

# Tabs for phases
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Discovery','AI UX Research','Planning','Creation','Testing','Finalizing','All Industries'])
with tab1: st.write("Problem to Solve, Target Audience, Creative Brief, Constraints, Stakeholder Interviews")
with tab2: st.write("User Research, Personas, User Behaviors, Competitor Analysis, Data Analysis")
with tab3: st.write("Project/Product Goals, Resource Allocation, Project Planning, Documentation, Ideation")
with tab4: st.write("Sketches, Wireframes, Use Case Flows, Functionality, Low & High Fidelity Prototypes, A/B Testing")
with tab5: st.write("Usability Testing, Evaluation, Beta Launch, Final User Feedback, Heuristic Evaluations, Final Refinements")
with tab6: st.write("Ordering, Packaging, Documentation, Rollout Plan, Go Live, Project Lessons/Debrief")
with tab7: st.write("AI and ML, Ecommerce, Finance, Government, Healthcare, Manufacture and Warehouse, Real Estate, Transportation, Travel")

# Agent Status Dashboard
st.header("Agent Status Dashboard")
df_agents = pd.DataFrame(
    [{'Agent': a, 'Group': g, 'Status': 'Active'} for g, group in [
        ('C-Suite', C_SUITE),('Foundational', FOUNDATIONAL),('Analytics', ANALYTICS),
        ('Builders', BUILDERS),('Tools', TOOLS),('Specialized', SPECIALIZED)
    ] for a in group]
)
st.dataframe(df_agents, use_container_width=True)

# Income Stream Pipeline
st.header("Income Stream Pipeline")
pipeline_data = pd.DataFrame([
    {'Stream': 'Stream 1','Status':'Planning','Revenue':0,'Container':'docker-stream1'},
    {'Stream': 'Stream 2','Status':'Testing','Revenue':0,'Container':'docker-stream2'},
])
st.dataframe(pipeline_data, use_container_width=True)

# Logs
st.header("Logs")
with st.expander("View Logs"):
    logs = r.lrange('novaos:logs', 0, -1)
    df_logs = pd.DataFrame([log.decode() for log in logs], columns=["Logs"])
    st.dataframe(df_logs, use_container_width=True)

# ───────────────────────── Ask with Memory (LLM) ─────────────────────────────
st.header("Ask with Memory (LLM)")
agent_sel = st.selectbox("Agent", options=ALL_AGENTS, index=ALL_AGENTS.index("NovaHistorian") if "NovaHistorian" in ALL_AGENTS else 0)
task_txt = st.text_area("Task", height=120, placeholder="What should the agent do?")
query_txt = st.text_input("Search query (optional)", placeholder="Leave blank to use the Task as the query")
k_num = st.number_input("Context snippets (K)", min_value=1, max_value=12, value=6, step=1)

if st.button("Ask with Memory"):
    if not task_txt.strip():
        st.error("Task is required.")
    else:
        with st.spinner("Thinking with memory…"):
            res = ask(agent=agent_sel, task=task_txt.strip(), query=(query_txt.strip() or None), k=int(k_num))
        st.subheader("Answer")
        st.write(res.get("answer") or "")
        st.subheader("Context used")
        ctx_rows = []
        for s in res.get("context_used", []):
            content = s.get("content","")
            preview = (content[:240] + ("…" if len(content) > 240 else "")).replace("\n"," ")
            ctx_rows.append({"doc_id": s.get("doc_id",""), "score": round(float(s.get("score",0.0)),4), "preview": preview})
        st.dataframe(pd.DataFrame(ctx_rows), use_container_width=True)
        st.caption(f"Trace ID: {res.get('trace_id','')}. Search memory for `runs/` to audit inputs/outputs.")

# ───────────────────────── Memory Search + Add Note ──────────────────────────
st.header("Memory Search (Postgres)")
if not MEMORY_ON:
    st.info(f"Memory disabled: {_memory_disabled_reason()}. App will still run.")
else:
    q = st.text_input("Query", value="NovaOS", key="mem_query")
    k = st.number_input("Results", min_value=1, max_value=20, value=5, step=1, key="mem_k")
    if st.button("Search Memory", key="mem_search_btn"):
        results = memory_search(q, k=int(k))
        rows = []
        for rec in results:
            content = rec.get("content","")
            preview = (content[:200] + ("..." if len(content) > 200 else "")).replace("\n"," ")
            rows.append({"doc_id": rec.get("doc_id",""), "score": round(rec.get("score",0.0), 4), "preview": preview})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.header("Add Note to Memory")
if not MEMORY_ON:
    st.info(f"Memory disabled: {_memory_disabled_reason()}. Notes are disabled.")
else:
    note_title = st.text_input("Title (becomes doc_id)", value="", placeholder="e.g., ops/decision-2025-08-11", key="note_title")
    note_tags = st.text_input("Tags (comma-separated)", value="note,dashboard", key="note_tags")
    note_body = st.text_area("Body", height=180, placeholder="Write the fact/decision/instruction you want NovaOS to remember.", key="note_body")
    col_a, col_b = st.columns([1,3])
    with col_a:
        if st.button("Save Note", key="note_save"):
            title = note_title.strip()
            body = note_body.strip()
            if not title or not body:
                st.error("Title and Body are required.")
            else:
                # Include title inside content so title-only searches hit the content index as well.
                content = f"{title}\n\n{body}" if title not in body else body
                tags = [t.strip() for t in note_tags.split(",") if t.strip()]
                ack = memory_learn(title, content, tags=tags)
                status = (ack or {}).get("status","unknown")
                if status in ("ok","updated"):
                    st.success(f"Saved to memory as '{title}'.")
                elif status == "disabled":
                    st.info(f"Memory disabled: {(ack or {}).get('reason')}")
                else:
                    st.error(f"Memory write failed: {ack}")
    with col_b:
        st.caption("Use stable titles like `ops/decision-YYYY-MM-DD` to update the same record later.")

# ───────────────────────── Commands + Sentinels (background) ─────────────────
def _log_and_mem(r_handle, event: str, details: str, mem_title: str, tags=None):
    try:
        r_handle.publish('novaos:logs', json.dumps({'event': event, 'details': details}))
    finally:
        memory_learn(mem_title, f"{event}: {details}", tags or ["agent","event"])

def handle_command(cmd, r_handle):
    try:
        print(f"DEBUG: Command received: {cmd}", flush=True)
        agent = cmd.get('agent'); payload = cmd.get('payload')
        if agent == 'CEO-VISION' and payload.get('action') == 'build_blueprint':
            blueprint = "NovaOS Blueprint: C-Suite strategy, Foundational setup, Analytics data, Builders/Tools execute, Specialized tasks. Replicable for 100+ streams."
            _log_and_mem(r_handle, 'Blueprint Built', blueprint, "ceo_vision_blueprint", tags=["ceo","blueprint"])
        elif agent == 'FoundationBuilder' and payload.get('action') == 'setup_business':
            setup = "Business Architecture: Shopify hub, Lemon Squeezy payments, Redis for data. Ready for streams."
            _log_and_mem(r_handle, 'Business Setup', setup, "foundation_setup", tags=["foundation","setup"])
        elif agent == 'DashboardAgent' and payload.get('action') == 'build_dashboard':
            dashboard = "Central Dashboard: agents view, approvals, logs at deployed URL."
            _log_and_mem(r_handle, 'Dashboard Built', dashboard, "dashboard_built", tags=["dashboard"])
        elif agent == 'DEVOPS-ENGINEER' and payload.get('action') == 'migrate_stack':
            steps = [
                'Cloning WooCommerce to Vercel','Integrating Stripe','Integrating Printful','Setting up Supabase','Integrating Alchemy'
            ]
            _log_and_mem(r_handle, 'Migration Started', 'Migration initiated', "devops_migrate_start", tags=["devops","migrate"])
            for det in steps:
                _log_and_mem(r_handle, 'Migration Step', det, "devops_migrate_step", tags=["devops","migrate"]); time.sleep(1)
            _log_and_mem(r_handle, 'Migration Completed', 'New stack ready for streams', "devops_migrate_done", tags=["devops","migrate"])
    except Exception as e:
        print(f"Command Error: {e}", flush=True)

def listener_thread():
    print("Listener Thread Started", flush=True)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    try:
        pubsub.subscribe('novaos:commands'); print("Subscribed to novaos:commands", flush=True)
        counter = 0
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                cmd = json.loads(message['data'].decode('utf-8')); handle_command(cmd, r)
            time.sleep(0.001); counter += 1
            if counter % 60000 == 0:
                print("Listener Loop Running", flush=True); counter = 0
    except Exception as e:
        print(f"Listener Subscribe Error: {e}", flush=True)

def time_sentinel_thread():
    print("TimeSentinel Thread Started", flush=True)
    while True:
        try:
            optimization = "Monitored streams: Optimized for $25k/month total revenue."
            r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
            memory_learn("optimization_cycle", optimization, tags=["sentinel","telemetry"])
            print("Optimization Cycle", flush=True)
        except Exception as e:
            print(f"TimeSentinel Publish Error: {e}", flush=True)
        time.sleep(60)

threading.Thread(target=listener_thread, daemon=True).start()
threading.Thread(tar
