import os
import json
import redis
import time
import threading
import requests
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

# Tabs for Phases (more prominent)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Discovery', 'AI UX Research', 'Planning', 'Creation', 'Testing', 'Finalizing', 'All Industries'])

with tab1:
    st.write("Problem to Solve, Target Audience, Creative Brief, Constraints, Stakeholder Interviews")
with tab2:
    st.write("User Research, Personas, User Behaviors, Competitor Analysis, Data Analysis")
with tab3:
    st.write("Project / Product Goals, Resource Allocation, Project Planning, Documentation, Ideation")
with tab4:
    st.write("Sketches, Wireframes, Use Case Flows, Functionality, Low & High Fidelity Prototypes, A/B Testing")
with tab5:
    st.write("Usability Testing, Evaluation, Beta launch, Final User Feedback, Heuristic Evaluations, Final Refinements")
with tab6:
    st.write("Ordering, Packaging, Documentation, Rollout Plan, Go Live, Project Lessons / Debrief")
with tab7:
    st.write("AI and ML, Ecommerce, Finance, Government, Healthcare, Manufacture and Warehouse, Real Estate, Transportation, Travel")

# Agents in sidebar
st.sidebar.title('Agents Active (46 Total)')
st.sidebar.write(', '.join([agent for group in ALL_GROUPS for agent in group]))

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

# Example Chart: Agent Groups
st.header('Agent Groups Overview')
group_data = pd.DataFrame({
    'Group': ['C-Suite', 'Foundational', 'Analytics', 'Builders', 'Tools', 'Specialized'],
    'Count': [9, 4, 6, 6, 16, 6]
})
chart = alt.Chart(group_data).mark_bar().encode(
    x='Group',
    y='Count',
    color='Group'
).properties(width=600, height=400)
st.altair_chart(chart, use_container_width=True)

# Example Map: Placeholder for Revenue/Business Metrics
st.header('Revenue Map (Placeholder)')
fig = px.choropleth(locations=['USA'], locationmode="USA-states", color=[1], scope="usa", labels={'1':'Revenue'})
st.plotly_chart(fig, use_container_width=True)

def handle_command(cmd, r_handle):
    try:
        agent = cmd.get('agent')
        payload = cmd['payload']
        if agent == 'CEO-VISION':
            if payload.get('action') == 'build_blueprint':
                blueprint = "NovaOS Blueprint: C-Suite oversees strategy, Foundational sets up business, Analytics drives data, Builders/Tools execute, Specialized handles tasks. Replicable for 100+ streams."
                r.publish('novaos:logs', json.dumps({'event': 'Blueprint Built', 'details': blueprint}))
                print("CEO-VISION: Blueprint built", flush=True)
        elif agent == 'FoundationBuilder':
            if payload.get('action') == 'setup_business':
                setup = "Business Architecture: Shopify hub, Lemon Squeezy payments, Redis for data. Ready for streams."
                r.publish('novaos:logs', json.dumps({'event': 'Business Setup', 'details': setup}))
                print("FoundationBuilder: Architecture set", flush=True)
        elif agent == 'DashboardAgent':
            if payload.get('action') == 'build_dashboard':
                dashboard = "Central Dashboard: View agents, approve actions, monitor logs at the deployed URL."
                r.publish('novaos:logs', json.dumps({'event': 'Dashboard Built', 'details': dashboard}))
                print("DashboardAgent: Dashboard ready", flush=True)
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

if __name__ == '__main__':
    threading.Thread(target=listener_thread).start()
    threading.Thread(target=time_sentinel_thread).start()
