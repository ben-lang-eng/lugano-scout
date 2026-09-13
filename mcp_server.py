import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()
MYSWITZERLAND_API_KEY = os.getenv("MYSWITZERLAND_API_KEY")
if not MYSWITZERLAND_API_KEY:
    raise RuntimeError(
        "MYSWITZERLAND_API_KEY is missing — copy .env.example to .env and add "
        "your key."
    )

BASE_URL = "https://opendata.myswitzerland.io/v1"
HEADERS = {"x-api-key": MYSWITZERLAND_API_KEY}


mcp = FastMCP("lugano-scout-tools")

if __name__ == "__main__":
    mcp.run()
