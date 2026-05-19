from __future__ import annotations

import os

import google.generativeai as genai
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def _get_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_gemini_model():
    genai.configure(api_key=_get_env("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-1.5-flash")


def run_gemini_prompt(prompt: str) -> str:
    model = get_gemini_model()
    response = model.generate_content(prompt)
    return (response.text or "").strip()


def get_tavily_client() -> TavilyClient:
    return TavilyClient(api_key=_get_env("TAVILY_API_KEY"))
