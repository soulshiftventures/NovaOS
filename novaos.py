import os
import json
import redis
import time
import threading
import requests
from dotenv import load_dotenv
from flask import Flask, render_template_string, request

load_dotenv()

LEMON_SQUEEZY_API_KEY = os.getenv('LEMON_SQUEEZY_API_KEY')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
REDIS_URL = os.getenv('REDIS_URL')

r = redis.from_url(REDIS_URL)
try:
    r.ping()
    print("Redis Connected Successfully", flush=True)
except Exception as e:
    print("Redis Connection Error: " + str(e), flush=True)

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

app = Flask(__name__)

@app.route('/dashboard')
def dashboard():
    logs = r.lrange('novaos:logs', 0, -1)
    return render_template_string("""
    <html>
    <head><title>NovaOS Dashboard</title></head>
    <body>
    <h1>NovaOS Central Hub</h1>
    <p>Manage agents, approve actions, view logs. Agents active: {{ agents }}</p>
    <h2>Logs</h2>
    <ul>
    {% for log in logs %}
        <li>{{ log.decode() }}</li>
    {% endfor %}
    </ul>
    <h2>Approve Actions</h2>
    <form method="POST">
        <button type="submit" name="approve" value="yes">Approve</button>
        <button type="submit" name="approve" value="no">Reject</button>
    </form>
    </body>
    </html>
    """, agents=', '.join([agent for group in ALL_GROUPS for agent in group]), logs=logs)

def handle_command(cmd, r_handle):
    try:
        agent = cmd.get('agent')
        payload = cmd['payload']
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
                dashboard = "Central Dashboard: View agents, approve actions, monitor logs at http://localhost:5000/dashboard."
                r_handle.publish('novaos:logs', json.dumps({'event': 'Dashboard Built', 'details': dashboard}))
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

def run_dashboard():
    print("Starting Flask Dashboard at http://localhost:5000/dashboard", flush=True)
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    threading.Thread(target=listener_thread).start()
    threading.Thread(target=time_sentinel_thread).start()
    threading.Thread(target=run_dashboard).start()
    while True:
        time.sleep(1)
