import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("LLM_MODEL", "gemini-3.5-flash-lite")

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        _client = genai.Client(api_key=api_key)
    return _client


def llm_call(system_prompt: str, user_prompt: str) -> str:
    response = _get_client().models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    return response.text
