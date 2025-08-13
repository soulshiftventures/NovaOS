
# NovaOS Deployment & Operations Plan

## Overview
This plan details the steps to transition NovaOS onto a managed cloud CI/CD platform, streamline agent execution, and accelerate income-generating workflows.

---

## 1. Platform Selection
- **Primary Recommendation:** Render.com
- **Alternatives:** Dokku (VPS), Fly.io, K3s + FluxCD/ArgoCD

---

## 2. Repository & CI/CD Setup
1. **Connect GitHub Repo**
   - Use GitHub integration on Render
2. **Add `render.yaml`**
   ```yaml
   services:
     - type: web
       name: nova-core
       env: python
       plan: free
       branch: main
       buildCommand: docker build -t nova-core ./agents/NOVA-CORE
       startCommand: docker run nova-core
     - type: private_service
       name: redis
       plan: free
   ```
3. **Push & Verify**
   - Commit `render.yaml`
   - Push to `main`
   - Monitor auto-deploy on Render

---

## 3. Agent Orchestration
- **LangGraph Service:** Ensure `langgraph/` Dockerfile is included in `render.yaml`
- **MCP Containers:** Define each agent (CEO, CTO, Nova, R&D) as separate services
- **Inter-Service Networking:** Use internal hostnames (e.g. `redis`) for Redis, `nova-core` for core agent

---

## 4. Task Processing Workflow
1. **Queues:**  
   - `novaos:tasks` (Redis list)  
   - `novaos:results` (Redis list)
2. **Agent Loop (nova.py):** Continuously BLPOP and process tasks
3. **n8n Flows:** Trigger on Redis events or HTTP webhook integration
4. **Baserow Sync:** Use Baserow Cloud API for persistent task storage

---

## 5. Monitoring & Alerts
- **Render Dashboard:** Uptime, logs, restart events
- **Grafana (Phase 2):** Connect to Redis metrics, container metrics
- **Error Alerts:** Slack or SMS via n8n on container crashes or queue backlogs

---

## 6. Future R&D & Product Streams
- **R&D Agent:** Automate trend detection with a dedicated agent  
- **Productizer Agent:** Convert R&D output to actionable pipelines  
- **Text Integration:** Future Phase: SMS/Twilio integration for mobile tasks  
- **AI Monetization:** Agent-as-a-Service, subscription-based flows

---

## 7. Timeline & Milestones
| Phase                    | Timeline       | Deliverable                                |
|--------------------------|----------------|--------------------------------------------|
| Repository Connect       | Day 1          | GitHub → Render integration                |
| Core Agents Deployment   | Day 2          | CEO, CTO, Nova running on Render           |
| Task Workflow Testing    | Day 3          | Ping/Pong loop, n8n workflow triggered     |
| Monitoring Setup         | Day 4          | Grafana dashboard, alert channels          |
| Phase 2 Agents Onboard   | Week 2         | R&D, Productizer, SMS integration          |

---

## 8. Reference & Resources
- Render Guides: https://render.com/docs  
- Redis CLI: https://redis.io/commands/blpop  
- n8n Workflows: https://docs.n8n.io  
- Baserow API: https://baserow.io/docs/api-developer-guide  

---

*Keep this plan updated in your repo under `/docs/DeploymentPlan.md`.*
