## AI-First CRM – Healthcare Professional (HCP) Interaction Log Module

An end-to-end, **AI-First CRM interaction logging module** for Healthcare Professionals (HCPs), built as a submission-ready reference implementation. It combines:

- **FastAPI + SQLAlchemy + SQLite** backend (PostgreSQL supported via DATABASE_URL)
- **LangGraph agent** orchestrating tools
- **Groq LLM (`llama-3.3-70b-versatile`)** for reasoning, extraction, and recommendations
- **React + Redux** frontend with a modern **Inter**-based UI

This module focuses on the **HCP Interaction Log Screen** with **two modes**:

- **Structured Form Mode** – deterministic data capture
- **Conversational Chat Mode** – free-text capture with AI extraction and confirmation

---

### Business Overview

- **Users**: Pharma / MedTech field sales reps and MSLs capturing interactions with HCPs.
- **Problem**: Manual, structured logging is slow and incomplete. Free-text notes are unstructured and not analytics-ready.
- **Solution**: An AI-first logging experience that:
  - Lets reps choose between a **structured form** and **conversational chat**.
  - Uses Groq LLM (via LangGraph agent) to **summarize**, **extract entities**, and **recommend next best actions**.
  - Stores data in a SQL database suitable for CRM integration.

---

## Architecture Overview

- **Frontend** (`frontend/`):
  - **React + Redux** SPA.
  - Two main components:
    - `LogInteractionForm.jsx` – structured interaction form.
    - `LogInteractionChat.jsx` – conversational AI-assisted logging.
  - Global Inter font from Google Fonts.
  - Uses **Axios** to call FastAPI APIs.

- **Backend** (`backend/`):
  - **FastAPI** application in `main.py`.
  - **SQLAlchemy** ORM models in `models/models.py`.
  - **SQLite** database by default (`sqlite:///./ai_first_crm_hcp.db`), with PostgreSQL support via `DATABASE_URL`.
  - Schema defined in `models/models.py` (SQLAlchemy ORM) and reference SQL in `database/schema.sql`.
  - **LangGraph agent** in `agents/hcp_agent.py`:
    - Handles intent classification via Groq LLM.
    - Routes to 5 dedicated tools in `backend/tools/`.
  - **Groq LLM** usage isolated in `llm_client.py`.

- **Database** (`database/`):
  - Tables:
    - `hcp_profiles` – HCP master data.
    - `interactions` – individual interaction logs with AI-enriched fields.

---

## Clean Architecture & Responsibilities

- **Presentation Layer (Frontend)**:
  - `App.jsx`:
    - High-level layout and **mode toggle** (Form vs Chat).
  - `LogInteractionForm.jsx`:
    - Collects structured fields: HCP name, specialty, date, channel, products, notes.
    - Sends **structured payload** to `/interactions/structured`.
  - `LogInteractionChat.jsx`:
    - Accepts **free-text interaction description**.
    - Calls `/interactions/chat`.
    - Renders **AI-extracted summary and entities** in a confirmation card.
  - `redux/interactionSlice.js`:
    - Central client state: mode, loading, errors, last interaction, chat tool result.

- **Application Layer (FastAPI Routes)**:
  - `routes/interaction.py`:
    - **POST `/interactions/structured`**
      - Saves structured payload directly to DB.
    - **POST `/interactions/chat`**
      - Invokes **LangGraph HCP agent** with the free-text input.
      - Returns tool result with **summary + entities**.
    - **PATCH `/interactions/{id}`**
      - Uses **edit_interaction tool** via the agent to update specific fields.
    - **GET `/interactions/{id}`**, **GET `/interactions`**
      - Return interaction(s) with HCP context.
    - **GET `/interactions/{id}/summary`**
      - Uses **generate_interaction_summary tool**.
    - **GET `/interactions/{id}/next-best-action`**
      - Uses **recommend_next_best_action tool**.

- **Domain Layer (Models & Tools)**:
  - `models/models.py`:
    - `HCPProfile`: core HCP information.
    - `Interaction`: core interaction log with AI-enriched fields (`summary`, `sentiment`, `follow_up_action`).
  - `tools/`:
    - **`log_interaction.py`**
    - **`edit_interaction.py`**
    - **`fetch_hcp_profile.py`**
    - **`generate_summary.py`**
    - **`next_best_action.py`**

- **Infrastructure Layer**:
  - `database.py` – SQLAlchemy engine and `get_db` dependency.
  - `llm_client.py` – Groq LLM client and helper functions.

---

## LangGraph Agent Design

**File**: `backend/agents/hcp_agent.py`

- **State type**: `AgentState` (a `TypedDict`):
  - `user_input`: latest user message (e.g., free-text notes).
  - `intent`: one of:
    - `log_interaction`
    - `edit_interaction`
    - `fetch_hcp_profile`
    - `generate_interaction_summary`
    - `recommend_next_best_action`
  - `tool_result`: result from the last tool invocation.
  - `context`: structured parameters (e.g., `interaction_id`, `updates`, `channel`).

- **Graph Nodes**:
  - `route_intent`:
    - Uses **Groq LLM** (system prompt + user input) to pick exactly one intent.
    - Returns one of the 5 tool labels.
  - Tool nodes:
    - `log_interaction` → `log_interaction_tool`
    - `edit_interaction` → `edit_interaction_tool`
    - `fetch_hcp_profile` → `fetch_hcp_profile_tool`
    - `generate_interaction_summary` → `generate_interaction_summary_tool`
    - `recommend_next_best_action` → `recommend_next_best_action_tool`

- **Graph Topology**:
  - Entry point: `route_intent`.
  - Edges:
    - `route_intent` → each of the 5 tool nodes.
    - Each tool node → `END`.

- **Runtime Integration**:
  - For each API call (e.g., `/interactions/chat`), FastAPI:
    - Constructs `AgentState` with `user_input` and `context`.
    - Builds the LangGraph `app` via `build_hcp_agent(db)`.
    - Streams through `app.stream(initial_state)` and reads the final `tool_result`.

---

## LangGraph Tools (5) – Detailed Description

All tools are pure Python functions that take a **SQLAlchemy `Session`** plus keyword arguments and return a **JSON-serializable dict**.

- **1️⃣ `log_interaction`** (`backend/tools/log_interaction.py`)
  - Input:
    - `free_text`: raw rep description of the interaction.
    - `channel` (optional).
    - `interaction_date` (optional).
  - Behavior:
    - Calls **Groq** (via `call_llm_structured`) with a strict JSON prompt to extract:
      - `hcp_name`
      - `specialty`
      - `products_discussed`
      - `sentiment`
      - `follow_up_action`
      - `summary`
    - Upserts an `HCPProfile` for (`hcp_name`, `specialty`).
    - Persists a new `Interaction` record with enriched fields.
  - Output:
    - Structured dict with IDs and all extracted fields.
  - Failure handling:
    - If JSON parsing fails, falls back to a minimal interaction using raw text.

- **2️⃣ `edit_interaction`** (`backend/tools/edit_interaction.py`)
  - Input:
    - `interaction_id`
    - `updates` dict (only allowed fields are applied).
  - Behavior:
    - Validates that the interaction exists.
    - Applies **whitelisted fields** only:
      - `interaction_date`, `channel`, `products_discussed`, `notes`,
        `summary`, `sentiment`, `follow_up_action`.
  - Output:
    - `{ success, interaction_id, applied_updates }`.

- **3️⃣ `fetch_hcp_profile`** (`backend/tools/fetch_hcp_profile.py`)
  - Input:
    - Either `hcp_id` or `hcp_name`.
  - Behavior:
    - Fetches HCP profile.
    - Attaches up to 5 recent interactions (id, date, channel, summary, products).
  - Output:
    - `{ success, hcp, recent_interactions }` or `{ success: false, error }`.

- **4️⃣ `generate_interaction_summary`** (`backend/tools/generate_summary.py`)
  - Input:
    - `interaction_id`.
  - Behavior:
    - Loads interaction + HCP context.
    - Calls **Groq** via `call_llm_system_prompt` to:
      - Generate a **CRM-ready, bullet-point style summary**.
  - Output:
    - `{ success, interaction_id, summary }`.

- **5️⃣ `recommend_next_best_action`** (`backend/tools/next_best_action.py`)
  - Input:
    - `interaction_id`.
  - Behavior:
    - Loads interaction + HCP context.
    - Calls **Groq** to suggest **2–3 concrete next best actions**.
    - Guidance includes being non-promotional and compliant-aware.
  - Output:
    - `{ success, interaction_id, recommendation }`.

---

## Groq LLM Usage

**File**: `backend/llm_client.py`

- Uses official **Groq Python SDK**:
  - `groq==0.11.0` (pinned in `backend/requirements.txt`).
  - Model: **`llama-3.3-70b-versatile`** (Groq-supported model).
- Key helpers:
  - `call_llm_system_prompt(system_prompt, user_content) -> str`
    - Classic system + user messaging.
  - `call_llm_structured(system_prompt, user_content, response_format) -> str`
    - Returns (LLM-generated) JSON string, parsed by caller.
- Configuration:
  - Requires environment variable: **`GROQ_API_KEY`**.
  - Throws a clear error if missing.
- Failure handling:
  - Exceptions wrapped into `RuntimeError("LLM call failed: ...")`.
  - `log_interaction` tool includes a **JSON parse fallback path** so the app remains usable even if the LLM response is malformed.

---

## Setup & Run Instructions

### 1. Prerequisites

- **Node.js** (18+ recommended).
- **Python** 3.10+ (tested on Python 3.13).
- **SQLite** (included with Python) - no additional database setup required.
  - For PostgreSQL production deployments, set `DATABASE_URL` environment variable.

---

### 2. Backend Setup (FastAPI + LangGraph + Groq)

From the project root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables (e.g. in `.env` or your shell):

```bash
# SQLite is used by default (no setup required)
# For PostgreSQL, uncomment and set:
# export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ai_first_crm_hcp"

export GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

**Note**: The database schema is automatically created on first run via SQLAlchemy ORM. No manual schema setup is required for SQLite. The SQLite database file (`ai_first_crm_hcp.db`) will be created in the project root when the application starts.

Run the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Verify health:

```bash
curl http://localhost:8000/health
```

---

### 3. Frontend Setup (React + Redux)

From the project root:

```bash
cd frontend
npm install
```

Optionally set the API base (default is `http://localhost:8000`):

```bash
export REACT_APP_API_BASE="http://localhost:8000"
```

Run the development server:

```bash
npm start
```

Open in your browser:

```text
http://localhost:3000
```

---

## Example User Flows

### Flow A – Structured Form Mode

1. User opens the app at `http://localhost:3000`.
2. **Mode toggle** is set to **Structured Form**.
3. User fills:
   - HCP Name
   - Specialty
   - Interaction Date
   - Channel (In-Person / Call / Virtual)
   - Products Discussed
   - Notes
4. User clicks **Save Interaction**.
5. Frontend sends payload to **POST `/interactions/structured`**.
6. Backend:
   - Ensures HCP profile exists.
   - Creates a new `interactions` record.
   - Returns interaction details.
7. UI displays **Last Saved Interaction** summary section.

### Flow B – Conversational Chat Mode (AI-first)

1. User toggles to **Conversational Chat**.
2. User selects **Channel** (e.g., Virtual).
3. User types a **free-text narrative**:
   - “Met Dr. Rossi virtually to discuss Product A; she was positive but requested outcome data…”
4. User clicks **Let AI Structure It**.
5. Frontend sends payload to **POST `/interactions/chat`**.
6. Backend:
   - Builds `AgentState` with `user_input` and `context`.
   - Invokes **LangGraph HCP agent**:
     - `route_intent` classifies intent as `log_interaction`.
     - `log_interaction` tool:
       - Calls **Groq LLM** to extract entities and summary.
       - Persists HCP + Interaction in DB.
       - Returns tool result.
7. Frontend renders:
   - **AI Extracted Summary**.
   - HCP name + specialty.
   - Products discussed.
   - Sentiment chip.
   - Follow-up action.
8. The UI message reminds the rep to treat this as a **confirmation step** before further CRM actions.

### Flow C – Next Best Action

1. (Optionally via your own extensions) call:
   - **GET `/interactions/{id}/next-best-action`**
2. FastAPI:
   - Builds agent with `user_input = "Recommend next best action"`.
   - Sets `context = { interaction_id }`.
   - Runs LangGraph agent:
     - `route_intent` selects `recommend_next_best_action`.
     - Tool calls **Groq** to produce **2–3 follow-up suggestions**.
3. Response body:
   - `{ success, interaction_id, recommendation }`.

---

## Video Demo Guidance

When recording a demo video, consider the following structure:

- **1. Introduction (30–60 seconds)**
  - Who the users are (HCP-facing reps / MSLs).
  - The problem with traditional CRM logging.
  - The AI-first approach using **LangGraph + Groq**.

- **2. Architecture Walkthrough (60–90 seconds)**
  - Show the folder structure.
  - Briefly explain:
    - `backend/agents/hcp_agent.py` – the orchestrating agent.
    - `backend/tools/*` – domain-specific tools.
    - `backend/llm_client.py` – Groq integration (llama-3.3-70b-versatile).
    - `frontend/src/components/*` – form and chat UIs.

- **3. Live Demo – Structured Form Mode (60–90 seconds)**
  - Fill out the form for a sample HCP and save.
  - Show the returned summary section.
  - Optional: briefly show the interaction record via `/docs` or a DB tool.

- **4. Live Demo – Conversational Chat Mode (2–3 minutes)**
  - Enter a realistic free-text interaction narrative.
  - Trigger AI processing and highlight:
    - Extracted **summary**.
    - **HCP name**, **specialty**, **products**, **sentiment**, **follow-up action**.
  - Emphasize that this came from a **LangGraph agent** + **Groq LLM**.

- **5. Next Best Action & Summary (60–90 seconds)**
  - Hit `/interactions/{id}/summary` and `/interactions/{id}/next-best-action` in Swagger UI or a small helper UI (if added).
  - Explain how these could feed:
    - Call planning.
    - CRM timelines.
    - Territory analytics.

- **6. Closing (30–60 seconds)**
  - Summarize business value.
  - Highlight extensibility:
    - Additional tools (e.g., objection handling, content suggestion).
    - Multi-channel HCP journey orchestration.

---

## Notes for Reviewers

- **Zero human-written data assumption**:
  - All structured fields are backed by SQL models.
  - All reasoning, summarization, and entity extraction are delegated to **Groq LLM** via explicit prompts.
- **Clean architecture & comments**:
  - Key modules contain descriptive docstrings and inline comments focused on **intent**, not just mechanics.
- **Extensibility**:
  - Additional LangGraph tools can be plugged into `hcp_agent.py` using the same pattern:
    - Define new tool in `backend/tools/`.
    - Add an intent label.
    - Extend `route_intent` system prompt and edges.

This project is **manager-review ready** and can serve as a foundation for a production-grade, AI-first HCP CRM interaction module. 

