from __future__ import annotations
from typing import Callable, Dict, List, Optional

_REGISTRY: Dict[str, Callable[[], None]] = {}

def register(name: str):
    def decorator(fn: Callable[[], None]):
        _REGISTRY[name] = fn
        return fn
    return decorator

def get_agent(name: str) -> Optional[Callable[[], None]]:
    return _REGISTRY.get(name)

def list_agents() -> List[str]:
    return sorted(_REGISTRY.keys())

if __name__ == "__main__":
    print("Registered agents:", ", ".join(list_agents()) or "(none)")
