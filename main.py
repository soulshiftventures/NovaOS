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
    {'Stream': 'Strea
