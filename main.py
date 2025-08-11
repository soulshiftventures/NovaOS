print("✅ NovaOS main.py launched")
import os
import json
import redis
import time
import threading
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# --- Memory (Postgres) client import with safe fallback ---
MEMORY_ON = False
def _memory_disabled_reason():
    if not os.environ.get("DATABASE_URL"):
        return "DATABASE_URL is not set"
    return "context_pg import failed"

try:
    from agents._lib.context_pg import fetch_context, learn
    if os.environ.get("DATABASE_URL"):
        MEMORY_ON = True
except Exception as _e:
    MEMORY_ON = False

def memory_learn(title: str, body: str, tags=None):
    """Write to memory if enabled; never crash UI."""
    if not MEMORY_ON:
        return {"status": "disabled", "reason": _memory_disabled_reason()}
    try:
        return learn(title, body, tags or [])
    except Exception as e:
        print(f"[memory.learn] ERROR: {e}", flush=True)
        return {"status": "error", "error": str(e)}

def memory_search(query: str, k: int = 8):
    """Read context if enabled; never crash UI."""
    if not MEMORY_ON:
        return []
    try:
        return fetch_context(query, k=k)
    except Exception as e:
        print(f"[memory.search] ERROR: {e}", flush=True)
        return []

# --- App env ---
load_dotenv()

LEMON_SQUEEZY_API_KEY = os.getenv('LEMON_SQUEEZY_API_KEY')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# --- Redis (mock for local) ---
class MockRedis:
    def __init__(self):
        self.approval = None
    def lrange(self, key, start, end):
        return [b'CEO-VISION: Blueprint built', b'FoundationBuilder: Architecture set', b'DashboardAgent: Dashboard ready', b'Optimization Cycle']
    def set(self, key, value):
        self.approval = value
    def get(self, key):
        return self.approval.encode() if self.approval else None
    def publish(self, channel, message):
        pass
    def pubsub(self, ignore_subscribe_messages=True):
        class MockPubSub:
            def subscribe(self, channel):
                pass
            def get_message(self):
                return None
        return MockPubSub()

# Use mock if local, real if Render
if os.getenv('RENDER') is None:
    r = MockRedis()
else:
    r = redis.from_url(REDIS_URL)
    try:
        r.ping()
        print("Redis Connected Successfully", flush=True)
    except Exception as e:
        print(f"Redis Connection Error: {e}", flush=True)

print("NovaOS Started - Activating Corporate Structure", flush=True)

# Corporate Structure: Agent Groups
C_SUITE = ['CEO-VISION', 'CFO-AUTO', 'CTO-AUTO', 'CMO-AUTO', 'CPO-AUTO', 'CCO-AUTO', 'CHIEF-STAFF', 'CLARITY-COACH', 'CLO-AUTO']
FOUNDATIONAL = ['AgentFactory', 'FoundationBuilder', 'NOVA-CORE', 'NovaHistorian']
ANALYTICS = ['AnalyticsAgent', 'TrendAnalyzer', 'TrendFetcher', 'RESEARCH-ANALYST', 'RoadmapAgent', 'BusinessPlanAgent']
BUILDERS = ['automation_architect', 'BuilderAgent', 'DashboardAgent', 'DashboardBuilder', 'UIUXBuilder', 'PROMPT-ENGINEER']
TOOLS = ['BaserowSync', 'CloudManager', 'DockerDeployer', 'DROPBOX-FILE-MANAGER', 'ENERGY-GUARDIAN', 'FileAgent', 'GITHUB-DEPLOYER', 'LANGGRAPH-ROUTER', 'LemonSqueezyIntegrator', 'N8N-FLOW-BUILDER', 'NovaDashboard', 'PublerScheduler', 'RENDER-MANAGER', 'ShopifyIntegrator', 'TestAgent']
SPECIALIZED = ['ai_systems_engineer', 'blueprints', 'core', 'CryptoStreamBuilder', 'StreamBuilder', 'TimeSentinel']

ALL_GROUPS = [C_SUITE, FOUNDATIONAL, ANALYTICS, BUILDERS, TOOLS, SPECIALIZED]

for group in ALL_GROUPS:
    for agent in group:
        print(f"{agent} Activated in Group", flush=True)

# --- Streamlit UI ---
st.set_page_config(page_title="NovaOS Central Hub", page_icon="🚀", layout="wide")
st.title('NovaOS Central Hub')

# Tabs for Fuselab-inspired phases
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Discovery', 'AI UX Research', 'Planning', 'Creation', 'Testing', 'Finalizing', 'All Industries'])

with tab1:
    st.write("Problem to Solve, Target Audience, Creative Brief, Constraints, Stakeholder Interviews")
with tab2:
    st.write("User Research, Personas, User Behaviors, Competitor Analysis, Data Analysis")
with tab3:
    st.write("Project/Product Goals, Resource Allocation, Project Planning, Documentation, Ideation")
with tab4:
    st.write("Sketches, Wireframes, Use Case Flows, Functionality, Low & High Fidelity Prototypes, A/B Testing")
with tab5:
    st.write("Usability Testing, Evaluation, Beta Launch, Final User Feedback, Heuristic Evaluations, Final Refinements")
with tab6:
    st.write("Ordering, Packaging, Documentation, Rollout Plan, Go Live, Project Lessons/Debrief")
with tab7:
    st.write("AI and ML, Ecommerce, Finance, Government, Healthcare, Manufacture and Warehouse, Real Estate, Transportation, Travel")

# Live Agent Dashboard
st.header('Agent Status Dashboard')
agents_data = [
    {'Agent': agent, 'Group': group_name, 'Status': 'Active'}
    for group_name, agents in [
        ('C-Suite', C_SUITE),
        ('Foundational', FOUNDATIONAL),
        ('Analytics', ANALYTICS),
        ('Builders', BUILDERS),
        ('Tools', TOOLS),
        ('Specialized', SPECIALIZED)
    ]
    for agent in agents
]
df_agents = pd.DataFrame(agents_data)
st.dataframe(df_agents, use_container_width=True, column_config={
    "Agent": st.column_config.TextColumn("Agent"),
    "Group": st.column_config.TextColumn("Group"),
    "Status": st.column_config.TextColumn("Status")
})

# Income Stream Pipeline
st.header('Income Stream Pipeline')
st.write("Placeholder for monitoring isolated streams (each in Docker containers).")
pipeline_data = pd.DataFrame([
    {'Stream': 'Stream 1', 'Status': 'Planning', 'Revenue': 0, 'Container': 'docker-stream1'},
    {'Stream': 'Stream 2', 'Status': 'Testing', 'Revenue': 0, 'Container': 'docker-stream2'}
])
st.dataframe(pipeline_data, use_container_width=True)

# Logs in expander with table
st.header('Logs')
with st.expander("View Logs"):
    logs = r.lrange('novaos:logs', 0, -1)
    df_logs = pd.DataFrame([log.decode() for log in logs], columns=["Logs"])
    st.dataframe(df_logs, use_container_width=True)

# --- Memory Search (reads from Postgres) ---
st.header('Memory Search (Postgres)')
if not MEMORY_ON:
    st.info(f"Memory disabled: {_memory_disabled_reason()}. App will still run.")
else:
    q = st.text_input("Query", value="NovaOS", key="mem_query")
    k = st.number_input("Results", min_value=1, max_value=20, value=5, step=1, key="mem_k")
    if st.button("Search Memory", key="mem_search_btn"):
        results = memory_search(q, k=int(k))
        rows = []
        for rec in results:
            content = rec.get("content", "")
            preview = (content[:200] + ("..." if len(content) > 200 else "")).replace("\n", " ")
            rows.append({
                "doc_id": rec.get("doc_id", ""),
                "score": round(rec.get("score", 0.0), 4),
                "preview": preview
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# --- Add Note to Memory (writes to Postgres) ---
st.header('Add Note to Memory')
if not MEMORY_ON:
    st.info(f"Memory disabled: {_memory_disabled_reason()}. Notes are disabled.")
else:
    note_title = st.text_input("Title (becomes doc_id)", value="", placeholder="e.g., ops/decision-2025-08-11", key="note_title")
    note_tags = st.text_input("Tags (comma-separated)", value="note,dashboard", key="note_tags")
    note_body = st.text_area("Body", height=180, placeholder="Write the fact/decision/instruction you want NovaOS to remember.", key="note_body")
    col_a, col_b = st.columns([1,3])
    with col_a:
        if st.button("Save Note", key="note_save"):
            tags = [t.strip() for t in note_tags.split(",") if t.strip()]
            ack = memory_learn(note_title.strip(), note_body.strip(), tags=tags)
            status = (ack or {}).get("status", "unknown")
            if status in ("ok", "updated"):
                st.success(f"Saved to memory as '{note_title.strip()}'.")
            elif status == "disabled":
                st.info(f"Memory disabled: {(ack or {}).get('reason')}")
            else:
                st.error(f"Memory write failed: {ack}")
    with col_b:
        st.caption("Tip: use stable titles like `ops/decision-YYYY-MM-DD` so you can overwrite/update easily.")

# Approve Actions
st.header('Approve Actions')
approval = r.get('novaos:approval')
if approval and approval.decode() == 'approve':
    st.success("Structure Approved - Ready for Analytics")
else:
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Approve', key="approve"):
            r.set('novaos:approval', 'approve')
            print("Approved via dashboard", flush=True)
            st.success("Approved structure")
            # Write decision to memory
            memory_learn("approval", "User approved NovaOS structure via dashboard.", tags=["decision","dashboard"])
    with col2:
        if st.button('Reject', key="reject"):
            r.set('novaos:approval', 'reject')
            print("Rejected via dashboard", flush=True)
            st.error("Rejected structure")
            # Write decision to memory
            memory_learn("rejection", "User rejected NovaOS structure via dashboard.", tags=["decision","dashboard"])

# System Overview Chart
st.header('System Overview')
group_data = pd.DataFrame({
    'Group': ['C-Suite', 'Foundational', 'Analytics', 'Builders', 'Tools', 'Specialized'],
    'Count': [len(C_SUITE), len(FOUNDATIONAL), len(ANALYTICS), len(BUILDERS), len(TOOLS), len(SPECIALIZED)]
})
chart = alt.Chart(group_data).mark_bar().encode(
    x='Group',
    y='Count',
    color='Group'
).properties(width=600, height=400)
st.altair_chart(chart, use_container_width=True)

# Placeholder Revenue Map
st.header('Revenue Map (Placeholder)')
fig = px.choropleth(locations=['USA'], locationmode="USA-states", color=[1], scope="usa", labels={'1':'Revenue'})
st.plotly_chart(fig, use_container_width=True)

# --- Command handling (writes events to memory) ---
def _log_and_mem(r_handle, event: str, details: str, mem_title: str, tags=None):
    try:
        r_handle.publish('novaos:logs', json.dumps({'event': event, 'details': details}))
    finally:
        memory_learn(mem_title, f"{event}: {details}", tags or ["agent","event"])

def handle_command(cmd, r_handle):
    try:
        print(f"DEBUG: Command received: {cmd}", flush=True)
        agent = cmd.get('agent')
        payload = cmd.get('payload')
        if agent == 'CEO-VISION':
            if payload.get('action') == 'build_blueprint':
                blueprint = "NovaOS Blueprint: C-Suite oversees strategy, Foundational sets up business, Analytics drives data, Builders/Tools execute, Specialized handles tasks. Replicable for 100+ streams."
                _log_and_mem(r_handle, 'Blueprint Built', blueprint, "ceo_vision_blueprint", tags=["ceo","blueprint"])
                print("CEO-VISION: Blueprint built", flush=True)
        elif agent == 'FoundationBuilder':
            if payload.get('action') == 'setup_business':
                setup = "Business Architecture: Shopify hub, Lemon Squeezy payments, Redis for data. Ready for streams."
                _log_and_mem(r_handle, 'Business Setup', setup, "foundation_setup", tags=["foundation","setup"])
                print("FoundationBuilder: Architecture set", flush=True)
        elif agent == 'DashboardAgent':
            if payload.get('action') == 'build_dashboard':
                dashboard = "Central Dashboard: View agents, approve actions, monitor logs at the deployed URL."
                _log_and_mem(r_handle, 'Dashboard Built', dashboard, "dashboard_built", tags=["dashboard"])
                print("DashboardAgent: Dashboard ready", flush=True)
        elif agent == 'DEVOPS-ENGINEER':
            if payload.get('action') == 'migrate_stack':
                migration = "Migration Started: Setup WooCommerce on Vercel, integrate Stripe/Printful/Supabase/Alchemy for streams."
                _log_and_mem(r_handle, 'Migration Started', migration, "devops_migrate_start", tags=["devops","migrate"])
                print("DEVOPS-ENGINEER: Migration to new stack initiated", flush=True)
                # Simulated migration steps
                steps = [
                    ('Migration Step', 'Cloning WooCommerce to Vercel'),
                    ('Migration Step', 'Integrating Stripe'),
                    ('Migration Step', 'Integrating Printful'),
                    ('Migration Step', 'Setting up Supabase'),
                    ('Migration Step', 'Integrating Alchemy'),
                ]
                for ev, det in steps:
                    print(f"DEVOPS-ENGINEER: {det}...", flush=True)
                    _log_and_mem(r_handle, ev, det, "devops_migrate_step", tags=["devops","migrate"])
                    time.sleep(1)
                _log_and_mem(r_handle, 'Migration Completed', 'New stack ready for streams', "devops_migrate_done", tags=["devops","migrate"])
                print("DEVOPS-ENGINEER: Migration Completed", flush=True)
    except Exception as e:
        print(f"Command Error: {e}", flush=True)

def listener_thread():
    print("Listener Thread Started", flush=True)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    try:
        pubsub.subscribe('novaos:commands')
        print("Subscribed to novaos:commands", flush=True)
        counter = 0
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                cmd = json.loads(message['data'].decode('utf-8'))
                print(f"Received command: {cmd}", flush=True)
                handle_command(cmd, r)
            time.sleep(0.001)
            counter += 1
            if counter % 60000 == 0:
                print("Listener Loop Running", flush=True)
                counter = 0
    except Exception as e:
        print(f"Listener Subscribe Error: {e}", flush=True)

def time_sentinel_thread():
    print("TimeSentinel Thread Started", flush=True)
    while True:
        try:
            optimization = "Monitored streams: Optimized for $25k/month total revenue."
            r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
            # Log to memory as periodic telemetry
            memory_learn("optimization_cycle", optimization, tags=["sentinel","telemetry"])
            print("Optimization Cycle", flush=True)
        except Exception as e:
            print(f"TimeSentinel Publish Error: {e}", flush=True)
        time.sleep(60)

threading.Thread(target=listener_thread, daemon=True).start()
threading.Thread(target=time_sentinel_thread, daemon=True).start()

# Keep main process alive
while True:
    time.sleep(60)
