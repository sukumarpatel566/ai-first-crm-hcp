from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.agents.hcp_agent import build_hcp_agent, AgentState
from backend.database import get_db
from backend.models.models import Interaction, HCPProfile


router = APIRouter(prefix="/interactions", tags=["interactions"])


class StructuredInteractionRequest(BaseModel):
    hcp_name: str
    specialty: Optional[str] = None
    interaction_date: datetime
    channel: str = Field(..., description="In-Person / Call / Virtual")
    products_discussed: Optional[str] = None
    notes: Optional[str] = None


class ChatInteractionRequest(BaseModel):
    free_text: str
    channel: Optional[str] = None
    interaction_date: Optional[datetime] = None


class InteractionResponse(BaseModel):
    id: int
    hcp_name: str
    specialty: Optional[str]
    interaction_date: datetime
    channel: str
    products_discussed: Optional[str]
    notes: Optional[str]
    summary: Optional[str]
    sentiment: Optional[str]
    follow_up_action: Optional[str]


def _ensure_hcp(db: Session, name: str, specialty: Optional[str]) -> HCPProfile:
    hcp = (
        db.query(HCPProfile)
        .filter(HCPProfile.name == name, HCPProfile.specialty == specialty)
        .first()
    )
    if not hcp:
        hcp = HCPProfile(name=name, specialty=specialty)
        db.add(hcp)
        db.flush()
    return hcp


@router.post("/structured", response_model=InteractionResponse)
def log_structured_interaction(
    payload: StructuredInteractionRequest, db: Session = Depends(get_db)
):
    """
    Structured Form Mode endpoint.
    Stores the interaction and returns enriched interaction data.
    """
    hcp = _ensure_hcp(db, payload.hcp_name, payload.specialty)

    interaction = Interaction(
        hcp_id=hcp.id,
        interaction_date=payload.interaction_date,
        channel=payload.channel,
        products_discussed=payload.products_discussed,
        notes=payload.notes,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return InteractionResponse(
        id=interaction.id,
        hcp_name=hcp.name,
        specialty=hcp.specialty,
        interaction_date=interaction.interaction_date,
        channel=interaction.channel,
        products_discussed=interaction.products_discussed,
        notes=interaction.notes,
        summary=interaction.summary,
        sentiment=interaction.sentiment,
        follow_up_action=interaction.follow_up_action,
    )


@router.post("/chat", response_model=Dict[str, Any])
def log_chat_interaction(
    payload: ChatInteractionRequest, db: Session = Depends(get_db)
):
    """
    Conversational Chat Mode endpoint.
    Delegates to the LangGraph HCP agent which in turn uses the log_interaction tool.
    The frontend is expected to confirm with the user before persisting in the UI flow.
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        if not payload.free_text or not payload.free_text.strip():
            raise HTTPException(
                status_code=400,
                detail="free_text is required and cannot be empty"
            )
        
        logger.info(f"Processing chat interaction: {payload.free_text[:100]}...")
        
        agent = build_hcp_agent(db)

        initial_state: AgentState = {
            "user_input": payload.free_text,
            "context": {
                "channel": payload.channel or "Meeting",
                "interaction_date": payload.interaction_date or datetime.utcnow(),
            },
        }

        # Run the agent; we take the final state from the generator
        final_state: AgentState = {}
        try:
            for step in agent.stream(initial_state):
                # step is an iterator of events; the last one contains the full state
                for node_name, state in step.items():
                    final_state = state  # overwrite until the end
                    logger.debug(f"Agent step: {node_name}, state keys: {list(state.keys())}")
        except Exception as agent_error:
            logger.error(f"Agent execution error: {agent_error}", exc_info=True)
            return {
                "error": True,
                "message": f"Agent execution failed: {str(agent_error)}",
            }

        tool_result = final_state.get("tool_result")
        intent = final_state.get("intent", "log_interaction")
        
        # Ensure tool_result is always a dict
        if not isinstance(tool_result, dict):
            logger.warning(f"tool_result is not a dict: {type(tool_result)}, value: {tool_result}")
            tool_result = {
                "error": True,
                "message": f"Unexpected tool result type: {type(tool_result)}",
            }
        
        logger.info(f"Agent completed with intent: {intent}, tool_result keys: {list(tool_result.keys()) if isinstance(tool_result, dict) else 'N/A'}")
        
        # If tool_result has error, return error response
        if isinstance(tool_result, dict) and tool_result.get("error"):
            return tool_result
        
        # Ensure we always return a valid structured dict response
        response = tool_result.copy() if isinstance(tool_result, dict) else {}
        response["status"] = "success"
        response["intent"] = intent
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in log_chat_interaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = (
        db.query(Interaction).filter(Interaction.id == interaction_id).first()
    )
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    hcp = db.query(HCPProfile).filter(HCPProfile.id == interaction.hcp_id).first()

    return InteractionResponse(
        id=interaction.id,
        hcp_name=hcp.name if hcp else "Unknown",
        specialty=hcp.specialty if hcp else None,
        interaction_date=interaction.interaction_date,
        channel=interaction.channel,
        products_discussed=interaction.products_discussed,
        notes=interaction.notes,
        summary=interaction.summary,
        sentiment=interaction.sentiment,
        follow_up_action=interaction.follow_up_action,
    )


@router.get("/", response_model=List[InteractionResponse])
def list_interactions(db: Session = Depends(get_db)):
    interactions = db.query(Interaction).order_by(Interaction.interaction_date.desc()).all()
    results: List[InteractionResponse] = []
    for i in interactions:
        hcp = db.query(HCPProfile).filter(HCPProfile.id == i.hcp_id).first()
        results.append(
            InteractionResponse(
                id=i.id,
                hcp_name=hcp.name if hcp else "Unknown",
                specialty=hcp.specialty if hcp else None,
                interaction_date=i.interaction_date,
                channel=i.channel,
                products_discussed=i.products_discussed,
                notes=i.notes,
                summary=i.summary,
                sentiment=i.sentiment,
                follow_up_action=i.follow_up_action,
            )
        )
    return results


class EditInteractionRequest(BaseModel):
    updates: Dict[str, Any]


@router.patch("/{interaction_id}", response_model=Dict[str, Any])
def edit_interaction(
    interaction_id: int, payload: EditInteractionRequest, db: Session = Depends(get_db)
):
    """
    Thin wrapper around the LangGraph tool for editing interactions.
    """
    agent = build_hcp_agent(db)
    initial_state: AgentState = {
        "user_input": "Edit interaction",
        "context": {"interaction_id": interaction_id, "updates": payload.updates},
    }

    final_state: AgentState = {}
    for step in agent.stream(initial_state):
        for _, state in step.items():
            final_state = state

    return final_state.get("tool_result") or {}


@router.get("/{interaction_id}/summary", response_model=Dict[str, Any])
def generate_summary(interaction_id: int, db: Session = Depends(get_db)):
    agent = build_hcp_agent(db)
    initial_state: AgentState = {
        "user_input": "Generate interaction summary",
        "context": {"interaction_id": interaction_id},
    }
    final_state: AgentState = {}
    for step in agent.stream(initial_state):
        for _, state in step.items():
            final_state = state

    return final_state.get("tool_result") or {}


@router.get("/{interaction_id}/next-best-action", response_model=Dict[str, Any])
def next_best_action(interaction_id: int, db: Session = Depends(get_db)):
    agent = build_hcp_agent(db)
    initial_state: AgentState = {
        "user_input": "Recommend next best action",
        "context": {"interaction_id": interaction_id},
    }
    final_state: AgentState = {}
    for step in agent.stream(initial_state):
        for _, state in step.items():
            final_state = state

    return final_state.get("tool_result") or {}

