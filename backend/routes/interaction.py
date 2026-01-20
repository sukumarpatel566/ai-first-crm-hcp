from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents.hcp_agent import build_hcp_agent, AgentState
from database import get_db
from models.models import Interaction, HCPProfile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interactions", tags=["interactions"])


# =========================
# Pydantic Models
# =========================

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


# =========================
# Helpers
# =========================

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


# =========================
# Routes
# =========================

@router.post("/structured", response_model=InteractionResponse)
def log_structured_interaction(
    payload: StructuredInteractionRequest,
    db: Session = Depends(get_db),
):
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


@router.post("/chat")
def log_chat_interaction(
    payload: ChatInteractionRequest,
    db: Session = Depends(get_db),
):
    if not payload.free_text.strip():
        raise HTTPException(status_code=400, detail="free_text cannot be empty")

    agent = build_hcp_agent(db)

    initial_state: AgentState = {
        "user_input": payload.free_text,
        "context": {
            "channel": payload.channel or "Meeting",
            "interaction_date": payload.interaction_date or datetime.utcnow(),
        },
    }

    final_state: AgentState = {}

    for step in agent.stream(initial_state):
        for _, state in step.items():
            final_state = state

    tool_result = final_state.get("tool_result")

    if not isinstance(tool_result, dict):
        raise HTTPException(
            status_code=500,
            detail="AI failed to extract structured data",
        )

    return {
        **tool_result,
        "status": "success",
        "intent": final_state.get("intent", "log_interaction"),
    }


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
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
    interactions = db.query(Interaction).order_by(
        Interaction.interaction_date.desc()
    ).all()

    results = []
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
