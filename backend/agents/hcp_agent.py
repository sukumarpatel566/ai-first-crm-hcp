"""
LangGraph Agent: HCP Interaction Manager

Single agent responsible for managing HCP interaction flows:
- Understands user intent (log / edit / summarize / profile / next best action)
- Routes to corresponding tools
- Maintains simple interaction state across turns
- Uses Groq LLM for high-level reasoning.
"""

from typing import Literal, TypedDict, Optional, Dict, Any

from langgraph.graph import StateGraph, END

from sqlalchemy.orm import Session

from backend.llm_client import call_llm_system_prompt
from backend.tools.log_interaction import log_interaction_tool
from backend.tools.edit_interaction import edit_interaction_tool
from backend.tools.fetch_hcp_profile import fetch_hcp_profile_tool
from backend.tools.generate_summary import generate_interaction_summary_tool
from backend.tools.next_best_action import recommend_next_best_action_tool


class AgentState(TypedDict, total=False):
    """
    Minimal shared state for the LangGraph agent.
    This can be extended as the CRM grows.
    """

    user_input: str
    intent: Literal[
        "log_interaction",
        "edit_interaction",
        "fetch_hcp_profile",
        "generate_interaction_summary",
        "recommend_next_best_action",
    ]
    tool_result: Dict[str, Any]
    context: Dict[str, Any]


def route_intent(state: AgentState) -> str:
    """
    Node: interpret user intent with Groq and decide which tool node to call.
    """
    user_input = state.get("user_input", "")
    context = state.get("context", {}) or {}

    system_prompt = (
        "You are an intent classifier for an AI-first CRM focused on HCP interactions.\n"
        "Map the user's request to EXACTLY one of these intents:\n"
        "- log_interaction\n"
        "- edit_interaction\n"
        "- fetch_hcp_profile\n"
        "- generate_interaction_summary\n"
        "- recommend_next_best_action\n\n"
        "Respond ONLY with the intent name, nothing else."
    )

    intent_raw = call_llm_system_prompt(system_prompt, user_input).strip()
    if intent_raw not in {
        "log_interaction",
        "edit_interaction",
        "fetch_hcp_profile",
        "generate_interaction_summary",
        "recommend_next_best_action",
    }:
        # Fallback to safest default: log_interaction
        intent_raw = "log_interaction"

    state["intent"] = intent_raw  # type: ignore[assignment]
    return intent_raw


def tool_log_interaction(state: AgentState, db: Session) -> AgentState:
    result = log_interaction_tool(
        db=db,
        free_text=state.get("user_input", ""),
        channel=state.get("context", {}).get("channel"),
        interaction_date=state.get("context", {}).get("interaction_date"),
    )
    state["tool_result"] = result
    return state


def tool_edit_interaction(state: AgentState, db: Session) -> AgentState:
    ctx = state.get("context") or {}
    interaction_id = ctx.get("interaction_id")
    updates = ctx.get("updates") or {}
    result = edit_interaction_tool(db=db, interaction_id=interaction_id, updates=updates)
    state["tool_result"] = result
    return state


def tool_fetch_hcp_profile(state: AgentState, db: Session) -> AgentState:
    ctx = state.get("context") or {}
    result = fetch_hcp_profile_tool(
        db=db, hcp_id=ctx.get("hcp_id"), hcp_name=ctx.get("hcp_name")
    )
    state["tool_result"] = result
    return state


def tool_generate_summary(state: AgentState, db: Session) -> AgentState:
    ctx = state.get("context") or {}
    interaction_id = ctx.get("interaction_id")
    result = generate_interaction_summary_tool(db=db, interaction_id=interaction_id)
    state["tool_result"] = result
    return state


def tool_next_best_action(state: AgentState, db: Session) -> AgentState:
    ctx = state.get("context") or {}
    interaction_id = ctx.get("interaction_id")
    result = recommend_next_best_action_tool(db=db, interaction_id=interaction_id)
    state["tool_result"] = result
    return state


def build_hcp_agent(db: Session):
    """
    Factory to construct a LangGraph compiled app for the HCP agent.
    The resulting app can be called like a function with an AgentState.
    """
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("route_intent", lambda state: route_intent(state))  # type: ignore[arg-type]
    workflow.add_node("log_interaction", lambda state: tool_log_interaction(state, db))
    workflow.add_node("edit_interaction", lambda state: tool_edit_interaction(state, db))
    workflow.add_node(
        "fetch_hcp_profile", lambda state: tool_fetch_hcp_profile(state, db)
    )
    workflow.add_node(
        "generate_interaction_summary",
        lambda state: tool_generate_summary(state, db),
    )
    workflow.add_node(
        "recommend_next_best_action",
        lambda state: tool_next_best_action(state, db),
    )

    # Entry point
    workflow.set_entry_point("route_intent")

    # Edges from router to tools
    workflow.add_edge("route_intent", "log_interaction")
    workflow.add_edge("route_intent", "edit_interaction")
    workflow.add_edge("route_intent", "fetch_hcp_profile")
    workflow.add_edge("route_intent", "generate_interaction_summary")
    workflow.add_edge("route_intent", "recommend_next_best_action")

    # All tools end the graph
    for node in [
        "log_interaction",
        "edit_interaction",
        "fetch_hcp_profile",
        "generate_interaction_summary",
        "recommend_next_best_action",
    ]:
        workflow.add_edge(node, END)

    app = workflow.compile()
    return app

