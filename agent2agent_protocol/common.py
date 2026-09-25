import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("LLM_MODEL", "gemini-3.5-flash-lite")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

client = genai.Client(api_key=GEMINI_API_KEY)


def llm_call(system_prompt: str, user_prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    return response.text
