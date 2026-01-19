from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class HCPProfile(Base):
    """
    Represents a Healthcare Professional (HCP) in the CRM.
    Stores basic profile/context used to personalize interactions.
    """

    __tablename__ = "hcp_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialty = Column(String(255), nullable=True, index=True)
    organization = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    interactions = relationship("Interaction", back_populates="hcp", lazy="selectin")


class Interaction(Base):
    """
    Represents a single interaction log with an HCP.
    This is the core entity for the HCP Interaction Module.
    """

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcp_profiles.id"), nullable=False, index=True)
    interaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    channel = Column(String(64), nullable=False)  # In-Person / Call / Virtual
    products_discussed = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # AI-enriched fields
    summary = Column(Text, nullable=True)
    sentiment = Column(String(64), nullable=True)
    follow_up_action = Column(Text, nullable=True)

    hcp = relationship("HCPProfile", back_populates="interactions")

