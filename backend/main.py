from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend.models.models import Base
from backend.routes.interaction import router as interaction_router


# Create all tables on startup (simple approach for a module demo).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First CRM – HCP Interaction Module",
    version="1.0.0",
    description="FastAPI backend with LangGraph + Groq-powered HCP interaction logging.",
)

# Allow local frontend development on common ports.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interaction_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

