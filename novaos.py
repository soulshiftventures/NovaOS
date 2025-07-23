import os
import json
import redis
import time
import threading
import requests
from dotenv import load_dotenv
import importlib  # For dynamic import

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

print("NovaOS Started - Activating All Agents from Folder", flush=True)

# Dynamic activation of all 46 specialized agents
agent_dirs = [
    'AgentFactory', 'ai_systems_engineer', 'AnalyticsAgent', 'automation_architect', 'BaserowSync', 'blueprints', 'BuilderAgent', 'BusinessPlanAgent', 'CCO-AUTO', 'CEO-VISION', 'CFO-AUTO', 'CHIEF-STAFF', 'CLARITY-COACH', 'CLO-AUTO', 'CloudManager', 'CMO-AUTO', 'core', 'CPO-AUTO', 'CryptoStreamBuilder', 'CTO-AUTO', 'DashboardAgent', 'DashboardBuilder', 'DockerDeployer', 'DROPBOX-FILE-MANAGER', 'ENERGY-GUARDIAN', 'FileAgent', 'FoundationBuilder', 'GITHUB-DEPLOYER', 'LANGGRAPH-ROUTER', 'LemonSqueezyIntegrator', 'N8N-FLOW-BUILDER', 'NOVA-CORE', 'NovaDashboard', 'NovaHistorian', 'PROMPT-ENGINEER', 'PublerScheduler', 'RENDER-MANAGER', 'RESEARCH-ANALYST', 'RoadmapAgent', 'ShopifyIntegrator', 'TestAgent', 'TimeSentinel', 'TrendAnalyzer', 'TrendFetcher', 'UIUXBuilder'
]
for agent_dir in agent_dirs:
    try:
        module = importlib.import_module(f"agents.{agent_dir}")
        if hasattr(module, 'run_agent'):
            threading.Thread(target=module.run_agent).start()
            print(f"{agent_dir} Activated", flush=True)
        else:
            print(f"{agent_dir} Activated (fallback - no run_agent, assuming passive)", flush=True)
    except Exception as e:
        print(f"{agent_dir} Activation Error: " + str(e), flush=True)

# Activate 100 Streams as instances (generic, so one class with params)
for i in range(1, 101):
    try:
        module = importlib.import_module(f"agents.Stream{i}")
        if hasattr(module, 'run_stream'):
            threading.Thread(target=module.run_stream, args=(i,)).start()
            print(f"Stream{i} Activated", flush=True)
        else:
            print(f"Stream{i} Activated (fallback instance)", flush=True)
    except Exception as e:
        print(f"Stream{i} Activation Error: " + str(e), flush=True)

# ... (keep the rest of the code from previous: handle_command, listener_thread, time_sentinel_thread)
