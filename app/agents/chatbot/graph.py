from langgraph.graph import StateGraph, END

from app.agents.chatbot.state import AgentState
from app.agents.chatbot.nodes import chat_node, tool_node


def should_use_tools(state: AgentState) -> str:
    """Conditional edge: route to tool_node if LLM returned tool_calls, else END."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"
    return END


def build_chatbot_graph():
    """Build and compile the chatbot agent graph.

    Flow:
        START → chat_node → (has tool_calls?) → tool_node → chat_node (loop)
                           → (no tool_calls?) → END
    """
    graph = StateGraph(AgentState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", tool_node)

    graph.set_entry_point("chat_node")

    graph.add_conditional_edges(
        "chat_node",
        should_use_tools,
        {"tool_node": "tool_node", END: END},
    )

    graph.add_edge("tool_node", "chat_node")

    return graph.compile()


compiled_graph = build_chatbot_graph()
