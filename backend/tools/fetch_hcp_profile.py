"""
LangGraph Tool: fetch_hcp_profile

Retrieves HCP context from the database, including recent interactions.
"""

from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session

from backend.models.models import HCPProfile, Interaction


def fetch_hcp_profile_tool(
    db: Session, *, hcp_id: Optional[int] = None, hcp_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch an HCP profile by ID or name, including a limited interaction history.
    """
    query = db.query(HCPProfile)
    if hcp_id is not None:
        query = query.filter(HCPProfile.id == hcp_id)
    elif hcp_name is not None:
        query = query.filter(HCPProfile.name.ilike(f"%{hcp_name}%"))
    else:
        return {"success": False, "error": "hcp_id or hcp_name must be provided"}

    hcp: Optional[HCPProfile] = query.first()
    if not hcp:
        return {"success": False, "error": "HCP not found"}

    interactions: List[Interaction] = (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp.id)
        .order_by(Interaction.interaction_date.desc())
        .limit(5)
        .all()
    )

    return {
        "success": True,
        "hcp": {
            "id": hcp.id,
            "name": hcp.name,
            "specialty": hcp.specialty,
            "organization": hcp.organization,
            "notes": hcp.notes,
        },
        "recent_interactions": [
            {
                "id": i.id,
                "interaction_date": i.interaction_date.isoformat(),
                "channel": i.channel,
                "summary": i.summary,
                "products_discussed": i.products_discussed,
            }
            for i in interactions
        ],
    }

