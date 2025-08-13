cat > ~/Desktop/NovaOS/agents/ShopifyIntegrator/main.py <<'EOF'
#!/usr/bin/env python3
import os, redis, time

r = redis.from_url(os.getenv("REDIS_URL"))
QUEUE = os.getenv("REDIS_QUEUE", "novaos:queue")

def run():
    while True:
        # BLPOP will block until an item arrives
        item = r.blpop(QUEUE, timeout=5)
        if item:
            _, data = item
            print(f"[Shopify-Integrator] Received: {data.decode()}")
            # TODO: call Shopify API here...
            # Acknowledge / forward if needed
        else:
            # no task in 5 seconds, continue waiting
            continue

if __name__ == "__main__":
    run()
EOF

chmod +x ~/Desktop/NovaOS/agents/ShopifyIntegrator/main.py
