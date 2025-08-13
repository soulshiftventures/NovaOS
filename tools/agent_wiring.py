#!/usr/bin/env python3
"""Agent wiring helpers (compile-safe skeleton)."""

from __future__ import annotations
from typing import Dict, Any, Callable

_REGISTRY: Dict[str, Callable[..., Any]] = {}

def register(name: str, fn: Callable[..., Any]) -> None:
    """Register an agent factory or handler."""
    _REGISTRY[name] = fn

def get_agent(name: str) -> Callable[..., Any] | None:
    """Fetch an agent by name."""
    return _REGISTRY.get(name)

def registry() -> Dict[str, Callable[..., Any]]:
    """Return the internal registry."""
    return dict(_REGISTRY)

# Temporary no-op wiring to satisfy compile checks
def wire_default_agents() -> None:
    pass

if __name__ == "__main__":
    wire_default_agents()
