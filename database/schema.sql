-- Database schema reference for AI-First CRM – HCP Interaction Module
-- 
-- NOTE: This file is for reference only. The actual schema is defined in
-- backend/models/models.py using SQLAlchemy ORM, which will automatically
-- create tables when the application starts (via Base.metadata.create_all).
--
-- The application uses SQLite by default (sqlite:///./ai_first_crm_hcp.db)
-- to avoid native build dependencies on Windows + Python 3.13.
--
-- For PostgreSQL production deployments, you can override DATABASE_URL:
-- DATABASE_URL=postgresql://user:password@localhost:5432/ai_first_crm_hcp

-- Table: hcp_profiles
-- Columns: id (PK), name, specialty, organization, notes

-- Table: interactions  
-- Columns: id (PK), hcp_id (FK), interaction_date, channel, products_discussed,
--          notes, summary, sentiment, follow_up_action

