# services/memory-api/app.py
"""
Compatibility wrapper for NovaOS memory API.

This file re-exports the FastAPI `app` from services/memory_api/app.py
(the underscore version). It lets your existing Render service continue
to point at services/memory-api without any changes to the start command.
"""

from services.memory_api.app import app
