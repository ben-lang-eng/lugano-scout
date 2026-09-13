import os

from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

GOOGLE_GEMINI = "gemini"
GEMINI_3POINT5_FLASH_LITE = "gemini-3.5-flash-lite"

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", GOOGLE_GEMINI)
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", GEMINI_3POINT5_FLASH_LITE)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MYSWITZERLAND_API_KEY = os.getenv("MYSWITZERLAND_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing — copy .env.example to .env and add "
        "your key."
    )
if not MYSWITZERLAND_API_KEY:
    raise RuntimeError(
        "MYSWITZERLAND_API_KEY is missing — copy .env.example to .env and "
        "add your key"
    )


def get_model():
    """Build the LLM instance selected by the MODEL_PROVIDER setting.

    The rest of the application never constructs a model directly — it
    always goes through this factory. Switching providers (e.g. Gemini
    to Apertus) is therefore a pure configuration change in `.env` plus
    one new branch here; no other code changes.

    Returns:
        Gemini: A configured agno model instance for the active provider.

    Raises:
        ValueError: If MODEL_PROVIDER names an unsupported provider.
    """
    if MODEL_PROVIDER == GOOGLE_GEMINI:
        return Gemini(id=GEMINI_MODEL_ID, api_key=GEMINI_API_KEY)
    else:
        raise ValueError(
            f"Unsupported MODEL_PROVIDER:{MODEL_PROVIDER!r}"
            f"(supported: 'gemini')"
        )
