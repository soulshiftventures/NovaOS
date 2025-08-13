#!/usr/bin/env python3
import os
import redis
import json
from datetime import datetime

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
QUEUE_KEY = 'novaos:commands'

AGENTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DASHBOARD_PATH = os.path.join(AGENTS_DIR, 'NovaDashboard')

def scaffold_dashboard(widgets):
    os.makedirs(os.path.join(DASHBOARD_PATH, 'app'), exist_ok=True)
    os.makedirs(os.path.join(DASHBOARD_PATH, 'components'), exist_ok=True)

    # Write app/page.tsx
    page_content = f"""
import QueueDepth from '../components/QueueDepth'
import TaskStream from '../components/TaskStream'

export default function Home() {{
  return (
    <main className="p-4">
      <h1 className="text-2xl mb-4">NovaOS Control Panel</h1>
      <QueueDepth />
      <TaskStream />
    </main>
  )
}}
""".strip()

    with open(os.path.join(DASHBOARD_PATH, 'app', 'page.tsx'), 'w') as f:
        f.write(page_content)

    # Write dummy widget components
    if 'QueueDepth' in widgets:
        with open(os.path.join(DASHBOARD_PATH, 'components', 'QueueDepth.tsx'), 'w') as f:
            f.write("export default function QueueDepth() { return <div>Queue Depth: [TODO]</div> }")

    if 'TaskStream' in widgets:
        with open(os.path.join(DASHBOARD_PATH, 'components', 'TaskStream.tsx'), 'w') as f:
            f.write("export default function TaskStream() { return <div>Task Stream: [TODO]</div> }")

    print(f"[DashboardBuilder] Scaffolded NovaDashboard with widgets: {widgets}")
    return {
        "status": "built",
        "folder": DASHBOARD_PATH,
        "widgets": widgets,
        "timestamp": datetime.utcnow().isoformat()
    }

def log_to_historian(agent_name, details):
    log = {
        "agent": agent_name,
        "action": "build",
        "details": details
    }
    message = json.dumps({
        "agent": "NovaHistorian",
        "payload": log
    })
    redis.from_url(REDIS_URL).publish(QUEUE_KEY, message)

def handle(payload):
    widgets = payload.get("widgets", ["QueueDepth", "TaskStream"])
    details = scaffold_dashboard(widgets)
    log_to_historian("DashboardBuilder", details)

def main():
    client = redis.from_url(REDIS_URL)
    pubsub = client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(QUEUE_KEY)
    print(f"[DashboardBuilder] Listening on Redis queue '{QUEUE_KEY}'...")

    for message in pubsub.listen():
        cmd = message.get('data')
        if isinstance(cmd, bytes):
            cmd = cmd.decode('utf-8')

        try:
            data = json.loads(cmd)
            if data.get('agent') == 'DashboardBuilder':
                print(f"[DashboardBuilder] Received: {data}")
                handle(data.get('payload', {}))
        except Exception as e:
            print(f"[DashboardBuilder] Error: {e}")

if __name__ == '__main__':
    main()

