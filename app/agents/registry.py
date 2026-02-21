from typing import Protocol
from langgraph.graph.state import CompiledStateGraph


class AgentProtocol(Protocol):
    """Protocol that all agents must implement."""

    def get_graph(self) -> CompiledStateGraph: ...


_registry: dict[str, CompiledStateGraph] = {}


def register_agent(name: str, graph: CompiledStateGraph) -> None:
    """Register a compiled agent graph by name."""
    _registry[name] = graph


def get_agent(name: str) -> CompiledStateGraph:
    """Retrieve a registered agent graph by name."""
    if name not in _registry:
        raise KeyError(
            f"Agent '{name}' not registered. Available: {list(_registry.keys())}"
        )
    return _registry[name]


def startup_agents() -> None:
    """Register all agents at application startup.

    Import and register each agent's compiled graph here.
    To add a new agent:
        1. Create agents/<name>/graph.py with a compiled_graph
        2. Import and register it below
    """
    from app.agents.chatbot.graph import compiled_graph as chatbot_graph

    register_agent("chatbot", chatbot_graph)
