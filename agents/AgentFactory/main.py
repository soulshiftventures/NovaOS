#!/usr/bin/env python3
import os
import redis
import json
import importlib.util

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
QUEUE_KEY = 'novaos:commands'

def load_agent(agent_name):
    """
    Dynamically load an agent module by name from the 'agents' folder.
    Each agent file must define a class 'Agent' with a 'handle' method.
    """
    module_path = os.path.join(os.path.dirname(__file__), 'agents', f'{agent_name}.py')
    spec = importlib.util.spec_from_file_location(agent_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Agent()

def dispatch(command):
    """
    Parse a JSON command with fields 'agent' and 'payload',
    load the corresponding agent, and invoke its handle() method.
    """
    data = json.loads(command)
    agent_name = data.get('agent')
    payload = data.get('payload', {})
    agent = load_agent(agent_name)
    agent.handle(payload)

def main():
    """
    Connect to Redis, subscribe to the command queue,
    and dispatch incoming commands to the appropriate agents.
    """
    client = redis.from_url(REDIS_URL)
    pubsub = client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(QUEUE_KEY)
    print(f"[AgentFactory] Listening on Redis queue '{QUEUE_KEY}'...")

    for message in pubsub.listen():
        cmd = message.get('data')
        if isinstance(cmd, bytes):
            cmd = cmd.decode('utf-8')
        print(f"[AgentFactory] Received raw command: {cmd}")
        try:
            dispatch(cmd)
        except Exception as e:
            print(f"[AgentFactory] Error handling command: {e}")

if __name__ == '__main__':
    main()

