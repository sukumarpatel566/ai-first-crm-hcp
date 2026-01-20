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

from llm_client import call_llm_system_prompt
from tools.log_interaction import log_interaction_tool
from tools.edit_interaction import edit_interaction_tool
from tools.fetch_hcp_profile import fetch_hcp_profile_tool
from tools.generate_summary import generate_interaction_summary_tool
from tools.next_best_action import recommend_next_best_action_tool



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


def route_intent(state: AgentState) -> AgentState:
    """
    Node: interpret user intent with Groq and decide which tool node to call.
    Returns the updated state dict.
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

    try:
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
    except Exception:
        # Fallback on LLM error
        intent_raw = "log_interaction"

    state["intent"] = intent_raw  # type: ignore[assignment]
    return state


def tool_log_interaction(state: AgentState, db: Session) -> AgentState:
    """
    Tool node: log interaction and format result as structured dict.
    """
    try:
        result = log_interaction_tool(
            db=db,
            free_text=state.get("user_input", ""),
            channel=state.get("context", {}).get("channel"),
            interaction_date=state.get("context", {}).get("interaction_date"),
        )
        
        # Format tool result as structured dict for frontend
        context = state.get("context", {})
        interaction_date = context.get("interaction_date")
        
        # Extract date and time if available
        from datetime import datetime
        date_str = ""
        time_str = ""
        if interaction_date:
            try:
                if isinstance(interaction_date, str):
                    # Parse ISO format string
                    dt = datetime.fromisoformat(interaction_date.replace("Z", "+00:00"))
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M")
                elif isinstance(interaction_date, datetime):
                    date_str = interaction_date.date().isoformat()
                    time_str = interaction_date.time().strftime("%H:%M")
                elif hasattr(interaction_date, "date"):
                    date_str = interaction_date.date().isoformat()
                    time_str = interaction_date.time().strftime("%H:%M")
                else:
                    date_str = str(interaction_date)
            except Exception as date_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Date parsing error: {date_error}")
                # Use current date/time as fallback
                now = datetime.utcnow()
                date_str = now.date().isoformat()
                time_str = now.time().strftime("%H:%M")
        
        # If date/time still empty, use current
        if not date_str:
            now = datetime.utcnow()
            date_str = now.date().isoformat()
            time_str = now.time().strftime("%H:%M")
        
        # Get channel from result or context
        channel = result.get("channel") or context.get("channel") or "Meeting"
        
        # Format structured response - ensure all fields are present
        formatted_result = {
            "hcp_name": result.get("hcp_name", "Unknown"),
            "interaction_type": channel,
            "date": date_str,
            "time": time_str,
            "summary": result.get("summary", ""),
            "topics": [t.strip() for t in (result.get("products_discussed") or "").split(",") if t.strip()],
            "sentiment": (result.get("sentiment") or "Neutral").capitalize(),
            "materials_shared": [],
            "samples_distributed": [],
            "follow_up_actions": [result.get("follow_up_action")] if result.get("follow_up_action") else [],
        }
        
        state["tool_result"] = formatted_result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in tool_log_interaction: {e}", exc_info=True)
        state["tool_result"] = {
            "error": True,
            "message": f"Failed to log interaction: {str(e)}",
        }
    
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
    workflow.add_node("route_intent", route_intent)
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

    # Conditional edges from router to tools based on intent
    # The conditional function extracts intent from state
    def get_intent(state: AgentState) -> str:
        return state.get("intent", "log_interaction")
    
    workflow.add_conditional_edges(
        "route_intent",
        get_intent,
        {
            "log_interaction": "log_interaction",
            "edit_interaction": "edit_interaction",
            "fetch_hcp_profile": "fetch_hcp_profile",
            "generate_interaction_summary": "generate_interaction_summary",
            "recommend_next_best_action": "recommend_next_best_action",
        },
    )

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

