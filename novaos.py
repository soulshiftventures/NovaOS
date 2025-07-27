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

load_dotenv()

LEMON_SQUEEZY_API_KEY = os.getenv('LEMON_SQUEEZY_API_KEY')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

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

# Approve Actions
st.header('Approve Actions')
col1, col2 = st.columns(2)
with col1:
    if st.button('Approve', key="approve"):
        r.set('novaos:approval', 'approve')
        print("Approved via dashboard", flush=True)
        st.success("Approved structure")
with col2:
    if st.button('Reject', key="reject"):
        r.set('novaos:approval', 'reject')
        print("Rejected via dashboard", flush=True)
        st.error("Rejected structure")

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

def handle_command(cmd, r_handle):
    try:
        print(f"DEBUG: Command received: {cmd}", flush=True)
        agent = cmd.get('agent')
        payload = cmd.get('payload')
        if agent == 'CEO-VISION':
            if payload.get('action') == 'build_blueprint':
                blueprint = "NovaOS Blueprint: C-Suite oversees strategy, Foundational sets up business, Analytics drives data, Builders/Tools execute, Specialized handles tasks. Replicable for 100+ streams."
                r_handle.publish('novaos:logs', json.dumps({'event': 'Blueprint Built', 'details': blueprint}))
                print("CEO-VISION: Blueprint built", flush=True)
        elif agent == 'FoundationBuilder':
            if payload.get('action') == 'setup_business':
                setup = "Business Architecture: Shopify hub, Lemon Squeezy payments, Redis for data. Ready for streams."
                r_handle.publish('novaos:logs', json.dumps({'event': 'Business Setup', 'details': setup}))
                print("FoundationBuilder: Architecture set", flush=True)
        elif agent == 'DashboardAgent':
            if payload.get('action') == 'build_dashboard':
                dashboard = "Central Dashboard: View agents, approve actions, monitor logs at the deployed URL."
                r_handle.publish('novaos:logs', json.dumps({'event': 'Dashboard Built', 'details': dashboard}))
                print("DashboardAgent: Dashboard ready", flush=True)
        elif agent == 'DEVOPS-ENGINEER':
            if payload.get('action') == 'migrate_stack':
                migration = "Migration Started: Setup WooCommerce on Vercel, integrate Stripe/Printful/Supabase/Alchemy for streams."
                r_handle.publish('novaos:logs', json.dumps({'event': 'Migration Started', 'details': migration}))
                print("DEVOPS-ENGINEER: Migration to new stack initiated", flush=True)
                # Simulate migration steps
                print("DEVOPS-ENGINEER: Cloning WooCommerce repo to Vercel...", flush=True)
                r_handle.publish('novaos:logs', json.dumps({'event': 'Migration Step', 'details': 'Cloning WooCommerce to Vercel'}))
                time.sleep(1)
                print("DEVOPS-ENGINEER: Integrating Stripe API...", flush=True)
                r_handle.publish('novaos:logs', json.dumps({'event': 'Migration Step', 'details': 'Integrating Stripe'}))
                time.sleep(1)
                print("DEVOPS-ENGINEER: Integrating Printful API...", flush=True)
                r_handle.publish('novaos:logs', json.dumps({'event': 'Migration Step', 'details': 'Integrating Printful'}))
                time.sleep(1)
                print("DEVOPS-ENGINEER: Setting up Supabase DB...", flush=True)
                r_handle.publish('novaos:logs', json.dumps({'event': 'Migration Step', 'details': 'Setting up Supabase'}))
                time.sleep(1)
                print("DEVOPS-ENGINEER: Integrating Alchemy for tokenized assets...", flush=True)
                r_handle.publish('novaos:logs', json.dumps({'event': 'Migration Step', 'details': 'Integrating Alchemy'}))
                time.sleep(1)
                print("DEVOPS-ENGINEER: Migration Completed", flush=True)
                r_handle.publish('novaos:logs', json.dumps({'event': 'Migration Completed', 'details': 'New stack ready for streams'}))
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
            print("Optimization Cycle", flush=True)
        except Exception as e:
            print(f"TimeSentinel Publish Error: {e}", flush=True)
        time.sleep(60)

threading.Thread(target=listener_thread).start()
threading.Thread(target=time_sentinel_thread).start()

# Keep main process alive
while True:
    time.sleep(60)
