from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the chatbot agent graph.

    messages: Full conversation history (managed by add_messages reducer).
    user_id:  Authenticated user's ID — used to scope all tool queries.
    """

    messages: Annotated[list, add_messages]
    user_id: int
