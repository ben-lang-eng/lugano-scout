import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "gemini")
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-3.5-flash-lite")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MYSWITZERLAND_API_KEY = os.getenv("MYSWITZERLAND_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing — copy .env.example to .env and add your key")
if not MYSWITZERLAND_API_KEY:
    raise RuntimeError("MYSWITZERLAND_API_KEY is missing — copy .env.example to .env and add your key")