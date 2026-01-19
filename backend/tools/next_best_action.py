"""
LangGraph Tool: recommend_next_best_action

Suggests follow-up actions based on interaction context and,
optionally, recent HCP history.
"""

from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.llm_client import call_llm_system_prompt
from backend.models.models import Interaction, HCPProfile


def recommend_next_best_action_tool(
    db: Session, *, interaction_id: int
) -> Dict[str, Any]:
    interaction: Optional[Interaction] = (
        db.query(Interaction).filter(Interaction.id == interaction_id).first()
    )
    if not interaction:
        return {"success": False, "error": "Interaction not found"}

    hcp: Optional[HCPProfile] = (
        db.query(HCPProfile).filter(HCPProfile.id == interaction.hcp_id).first()
    )

    system_prompt = (
        "You are an AI assistant for a pharma CRM, recommending the next best "
        "commercial action after an HCP interaction. You must stay non-promotional "
        "and aligned with typical medical/commercial compliance constraints.\n"
        "Return 2-3 concrete, actionable, short recommendations."
    )

    user_content = (
        f"HCP: {hcp.name if hcp else 'Unknown'} "
        f"(Specialty: {hcp.specialty if hcp else 'N/A'})\n"
        f"Last interaction channel: {interaction.channel}\n"
        f"Sentiment: {interaction.sentiment or 'N/A'}\n"
        f"Follow-up currently planned: {interaction.follow_up_action or 'None'}\n"
        f"AI summary: {interaction.summary or 'N/A'}\n"
        f"Raw notes: {interaction.notes or 'N/A'}\n\n"
        "Recommend the next best action for the rep."
    )

    nba = call_llm_system_prompt(system_prompt, user_content)

    return {
        "success": True,
        "interaction_id": interaction.id,
        "recommendation": nba,
    }

