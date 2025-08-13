# tools/agent_wiring.py
#!/usr/bin/env python3
"""
Agent wiring utilities (compile-safe stub).
This keeps CI's "python -m compileall" green while we iterate.
"""

from typing import Any, Dict

def wire_agent(name: str, **kwargs: Any) -> Dict[str, Any]:
    """Return a dummy spec to satisfy imports during CI."""
    return {"name": name, "config": kwargs}

def main() -> None:
    # Placeholder for manual testing
    pass

if __name__ == "__main__":
    main()
