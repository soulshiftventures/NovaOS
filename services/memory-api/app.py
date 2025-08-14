# services/memory-api/app.py
"""
Compatibility wrapper for NovaOS memory API.

This file re-exports the FastAPI `app` defined in services/memory_api/app.py.
It allows legacy deployment configurations that point to the hyphenated
directory to use the updated Supabase-backed memory API without changing
Render’s start command.
"""

from services.memory_api.app import app
