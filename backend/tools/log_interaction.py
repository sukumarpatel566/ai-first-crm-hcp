"""
LangGraph Tool: log_interaction

Uses Groq LLM to:
- Summarize the interaction
- Extract structured entities:
  - HCP Name
  - Products discussed
  - Sentiment
  - Follow-up action
- Persist data to SQL database.
"""

import json
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from backend.llm_client import call_llm_structured
from backend.models.models import HCPProfile, Interaction


def _build_extraction_prompt(free_text: str) -> str:
    return (
        "You are an assistant that extracts structured HCP interaction data for a CRM.\n"
        "Return a compact JSON object with exactly these fields:\n"
        "{\n"
        '  "hcp_name": string,\n'
        '  "specialty": string or null,\n'
        '  "products_discussed": string (comma-separated),\n'
        '  "sentiment": "positive" | "neutral" | "negative",\n'
        '  "follow_up_action": string,\n'
        '  "summary": string\n'
        "}\n\n"
        "Be concise but specific. Input interaction from the rep:\n\n"
        f"{free_text}"
    )


def log_interaction_tool(
    db: Session,
    *,
    free_text: str,
    channel: str | None = None,
    interaction_date: datetime | None = None,
) -> Dict[str, Any]:
    """
    Tool implementation.

    Args:
        db: SQLAlchemy session.
        free_text: Raw conversation/notes from the rep.
        channel: Communication channel if known.
        interaction_date: Optional explicit date; defaults to now.

    Returns:
        Dict describing the created interaction and extracted entities.
    """
    system_prompt = (
        "You are an AI assistant helping a pharma CRM system structure interaction logs "
        "with Healthcare Professionals (HCPs)."
    )
    user_prompt = _build_extraction_prompt(free_text)

    try:
        raw_response = call_llm_structured(system_prompt, user_prompt, response_format={})
    except Exception as llm_error:
        # If LLM call fails, use fallback data
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"LLM call failed, using fallback: {llm_error}")
        raw_response = None

    try:
        if raw_response:
            data = json.loads(raw_response)
        else:
            raise json.JSONDecodeError("No response from LLM", "", 0)
    except (json.JSONDecodeError, ValueError) as parse_error:
        # Fallback: store minimal interaction with raw text only.
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"JSON parse failed, using fallback: {parse_error}")
        data = {
            "hcp_name": "Unknown",
            "specialty": None,
            "products_discussed": None,
            "sentiment": "neutral",
            "follow_up_action": None,
            "summary": free_text[:500],
        }

    hcp_name = (data.get("hcp_name") or "Unknown").strip()
    specialty = (data.get("specialty") or None) or None

    # Find or create HCP profile
    hcp = (
        db.query(HCPProfile)
        .filter(HCPProfile.name == hcp_name, HCPProfile.specialty == specialty)
        .first()
    )
    if not hcp:
        hcp = HCPProfile(name=hcp_name, specialty=specialty)
        db.add(hcp)
        db.flush()

    interaction = Interaction(
        hcp_id=hcp.id,
        interaction_date=interaction_date or datetime.utcnow(),
        channel=channel or "Unknown",
        products_discussed=data.get("products_discussed"),
        notes=free_text,
        summary=data.get("summary"),
        sentiment=data.get("sentiment"),
        follow_up_action=data.get("follow_up_action"),
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return {
        "interaction_id": interaction.id,
        "hcp_id": hcp.id,
        "hcp_name": hcp.name,
        "specialty": hcp.specialty,
        "products_discussed": interaction.products_discussed,
        "sentiment": interaction.sentiment,
        "follow_up_action": interaction.follow_up_action,
        "summary": interaction.summary,
    }

