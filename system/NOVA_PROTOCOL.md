# NOVA_PROTOCOL.md – Persistent Build Rules for NovaOS

## ✅ NOVA INSTRUCTION SET (FOR ALL RESPONSES)

1. 📍 File + Directory Precision
   - Always state the exact working directory and file name before providing any code.
   - Example:
     📂 Location: /Users/krissanders/Desktop/NovaOS/main.py

2. ✅ Full File Replacements Only
   - Never request manual edits or partial inserts.
   - Always provide the **entire file contents** for copy-paste replacement.

3. 🧠 No Fake or Filler Code
   - No mockups or placeholder code.
   - Only real, verified logic relevant to NovaOS build.
   - Always confirm new values (Redis URLs, API keys, etc.) before use.

4. 🔒 Respect Render + GitHub Cloud Context
   - Primary execution environment: **Render** (https://dashboard.render.com/) with GitHub repo (https://github.com/soulshiftventures/NovaOS).
   - Local terminals are only used when explicitly stated.
   - Any changes to keys/URLs must include exact instructions for `.env`, Dockerfile, or Render settings.

5. 🧠 Clear Command Fields (for Terminal)
   - Distinguish guidance from commands.
   - Use ✅ COPY BELOW sections for exact shell commands.

6. 🧭 Always Clarify Operating Context
   - Confirm current working location before any step.
   - Label steps clearly (Step A, B, C) with zero skipped details.

7. 🧩 Respect Your Execution Model
   - No manual edits. Full, clean, copy-paste replacements only.

8. 🚫 No Assumptions About Knowledge Level
   - Instructions must be TBI-adapted, simple, and explicit.

9. 🔁 Keep Responses Fast and Lightweight
   - Avoid bloated messages that freeze chat.
   - Provide only actionable outputs.

10. 📦 System Truth Above All
   - Align all guidance to confirmed NovaOS architecture:
     - LangGraph agents
     - Redis queues
     - Dockerized streams
     - Render deployment.
   - Treat NovaOS as a real operational system.
