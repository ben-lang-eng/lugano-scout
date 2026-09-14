import os

from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAILike
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from dotenv import load_dotenv

load_dotenv()

GOOGLE_GEMINI = "gemini"
SWISSAI_APERTUS = "apertus"
GEMINI_3POINT5_FLASH_LITE = "gemini-3.5-flash-lite"
LAT_LUGANO = 46.005
LON_LUGANO = 8.953

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", GOOGLE_GEMINI)
APERTUS_BASE_URL = os.getenv("APERTUS_BASE_URL")
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", GEMINI_3POINT5_FLASH_LITE)
APERTUS_MODEL_ID = os.getenv("APERTUS_MODEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APERTUS_API_KEY = os.getenv("APERTUS_API_KEY")
MYSWITZERLAND_API_KEY = os.getenv("MYSWITZERLAND_API_KEY")
SEARCH_LAT = os.getenv("SEARCH_LAT", LAT_LUGANO)
SEARCH_LON = os.getenv("SEARCH_LON", LON_LUGANO)

INSTRUCTIONS = f"""\
You are Lugano Scout, an agent that finds accommodation deals around the 
given latitude/longitude (default is Lugano, TI, Switzerland).

## Search area
Search around {SEARCH_LAT},{SEARCH_LON} (Lugano, Ticino, Switzerland) by 
default. If the user names a different place, use that place's coordinates 
instead.

## Workflow
1. Search all available offers for the given location. This is a broad search 
   without query; dates and budget are filtered by YOU from the results, 
   never via the query parameter.
2. View results, keep only overnight stay offers, exclude experiences and 
    transfers.
3. Only extract offer details for the shortlist.
4. Rank the shortlist and respond with the ranked shortlist.


## Filtering the results
Only accommodation results should be considered. Experiences and transfers
should be removed. The offer validity date must be considered too.
Be sure to differentiate between total cost and cost per night.

## Output format
The output should be in tabular format.
Each row is one result. Each result should include the name, total cost in CHF,
cost per night in CHF, offer valid until and a link. If the offer is a 
package,add a column outlining its duration.
This format is adopted because it should be easy to read, contains key 
information but it is not overwhelming.

## Honesty rules
Mention if the offerings don't have any ratings and don't guarantee 
availability.
If there are no offers left after filtering, it is preferred that this is
honestly conveyed (and reasons why items were filtered out) rather than 
providing offers just for the sake of it.
"""


def validate_config():
    """Validates if the .env file provides a usable model provider, model id,
    api key, base url. Check if the datasource api key is usable.

    Raises a RuntimeError with the name of the missing .env item."""
    required = {"MYSWITZERLAND_API_KEY": MYSWITZERLAND_API_KEY}
    if MODEL_PROVIDER == GOOGLE_GEMINI:
        required["GEMINI_API_KEY"] = GEMINI_API_KEY
    elif MODEL_PROVIDER == SWISSAI_APERTUS:
        required["APERTUS_API_KEY"] = APERTUS_API_KEY
        required["APERTUS_BASE_URL"] = APERTUS_BASE_URL
        required["APERTUS_MODEL_ID"] = APERTUS_MODEL_ID
    for name, value in required.items():
        if not value:
            raise RuntimeError(
                f"{name} is missing — copy .env.example."
                f"Supported: {GOOGLE_GEMINI}, {SWISSAI_APERTUS}."
            )


validate_config()


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
    elif MODEL_PROVIDER == SWISSAI_APERTUS:
        return OpenAILike(
            id=APERTUS_MODEL_ID,
            api_key=APERTUS_API_KEY,
            base_url=APERTUS_BASE_URL,
            default_headers={"User-Agent": "lugano-scout/0.1"},
        )
    else:
        raise ValueError(
            f"Unsupported MODEL_PROVIDER:{MODEL_PROVIDER!r} "
            f"( supported: {GOOGLE_GEMINI}, {SWISSAI_APERTUS}.)"
        )


mcp_tools = MCPTools(command="python mcp_server.py")

lugano_agent = Agent(
    name="Lugano Scout",
    model=get_model(),
    tools=[mcp_tools],
    instructions=INSTRUCTIONS,
    markdown=True,
    add_datetime_to_context=True,
)

agent_os = AgentOS(agents=[lugano_agent])
app = agent_os.get_app()
