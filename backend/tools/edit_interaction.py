"""
LangGraph Tool: edit_interaction

Allows modification of existing interaction fields while keeping an audit-friendly
update path. Only mutable business fields are exposed via this tool.
"""

from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.models.models import Interaction


ALLOWED_FIELDS = {
    "interaction_date",
    "channel",
    "products_discussed",
    "notes",
    "summary",
    "sentiment",
    "follow_up_action",
}


def edit_interaction_tool(
    db: Session, *, interaction_id: int, updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update selected fields of an interaction.

    Args:
        db: SQLAlchemy session.
        interaction_id: ID of the interaction to update.
        updates: Dict of field -> new value.
    """
    interaction: Optional[Interaction] = (
        db.query(Interaction).filter(Interaction.id == interaction_id).first()
    )
    if not interaction:
        return {"success": False, "error": "Interaction not found."}

    applied = {}
    for field, value in updates.items():
        if field not in ALLOWED_FIELDS:
            continue
        setattr(interaction, field, value)
        applied[field] = value

    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return {
        "success": True,
        "interaction_id": interaction.id,
        "applied_updates": applied,
    }

