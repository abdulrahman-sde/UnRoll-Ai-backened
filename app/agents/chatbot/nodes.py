import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from app.core.config import settings
from app.agents.chatbot.state import AgentState
from app.agents.chatbot.tools import all_tools

logger = logging.getLogger(__name__)

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
)
llm_with_tools = llm.bind_tools(all_tools)

tool_node = ToolNode(all_tools)


async def chat_node(state: AgentState) -> dict:
    """Invoke the LLM with the system prompt and conversation history.

    The LLM decides whether to respond directly or call tools.
    If it returns tool_calls, the graph routes to tool_node.
    """
    messages = [SystemMessage(content=settings.CHATBOT_SYSTEM_PROMPT)] + state["messages"]
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}
