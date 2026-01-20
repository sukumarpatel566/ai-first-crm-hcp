"""
Centralized Groq LLM client and prompt utilities.
This isolates all LLM calls from business logic and tools.
"""

import os
from typing import List, Dict, Any

from groq import Groq

GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY environment variable required for Groq LLM."
        )
    return Groq(api_key=api_key)


def call_llm_system_prompt(system_prompt: str, user_content: str) -> str:
    """
    Helper to call Groq with a classic system+user prompt pattern.
    Returns the assistant message content as plain text.
    """
    client = _get_client()
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
    except Exception as exc:  # pragma: no cover - network failure path
        # In production, you might send this to observability tooling.
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    return completion.choices[0].message.content if completion.choices else ""


def call_llm_structured(
    system_prompt: str, user_content: str, response_format: Dict[str, Any]
) -> str:
    """
    Helper to call Groq expecting a JSON-like structured response.
    For simplicity we still return raw text and let the caller parse JSON.
    """
    client = _get_client()
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    return completion.choices[0].message.content if completion.choices else ""

