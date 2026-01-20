import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models.models import Base
from routes.interaction import router as interaction_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First CRM – HCP Interaction Module",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interaction_router)

@app.get("/health")
def health():
    return {"status": "ok"}
