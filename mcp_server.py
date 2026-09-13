import os

import httpx
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


@mcp.tool
def search_offers(latitude: float, longitude: float, radius_m: int = 15000,
                  query: str = "") -> list[dict]:
    """
    Searches through holiday and tourism offers (overnight stays, experiences 
    and transfers) around a given coordinate point with a given radius.
    Results must be semantically filtered.
    Returns a compact list of offers with id, name, price in CHF, 
    validity dates and URL
    """
    params = {"geo.dist": f"{latitude},{longitude},{radius_m}",
              "hitsPerPage": 50}
    if query:
        params["query"] = query
    response = httpx.get(f"{BASE_URL}/offers", params=params, headers=HEADERS,
                         timeout=20)
    response.raise_for_status()

    results = []
    for offer in response.json()["data"]:
        results.append(
            {
                "id": offer.get("identifier"),
                "name": offer.get("name"),
                "min_price_chf": (
                    offer.get("priceSpecification") or {}
                ).get("minPrice"),
                "valid_from": offer.get("validFrom"),
                "valid_through": offer.get("validThrough"),
                "url": offer.get("url"),
            }
        )
    return results


if __name__ == "__main__":
    mcp.run()
