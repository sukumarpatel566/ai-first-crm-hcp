"""
LangGraph Tool: generate_interaction_summary

Creates a rep-friendly, CRM-ready summary of an interaction
using the Groq LLM, optionally enriched with HCP context.
"""

from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.llm_client import call_llm_system_prompt
from backend.models.models import Interaction, HCPProfile


def generate_interaction_summary_tool(
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
        "You are an assistant creating concise, CRM-ready summaries for pharma sales "
        "reps after interactions with Healthcare Professionals (HCPs).\n"
        "Use bullet points where helpful, and highlight key messages, objections, and "
        "follow-up needs."
    )

    user_content = (
        f"HCP: {hcp.name if hcp else 'Unknown'} "
        f"(Specialty: {hcp.specialty if hcp else 'N/A'})\n"
        f"Channel: {interaction.channel}\n"
        f"Date: {interaction.interaction_date.isoformat()}\n"
        f"Products discussed: {interaction.products_discussed or 'N/A'}\n"
        f"Existing AI summary: {interaction.summary or 'N/A'}\n"
        f"Raw notes: {interaction.notes or 'N/A'}\n\n"
        "Create a short, rep-friendly summary suitable for a CRM timeline."
    )

    summary = call_llm_system_prompt(system_prompt, user_content)

    return {
        "success": True,
        "interaction_id": interaction.id,
        "summary": summary,
    }

