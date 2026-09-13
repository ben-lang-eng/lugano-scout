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
def search_offers(
    latitude: float, longitude: float, radius_m: int = 15000, query: str = ""
) -> list[dict]:
    """Search tourism offers around a coordinate point.

    The offers mix overnight-stay deals, experiences and transfers under
    a single classification, so callers must filter the results
    semantically (e.g. keep only overnight stays).

    Args:
        latitude: Latitude of the search-area centre (WGS84).
        longitude: Longitude of the search-area centre (WGS84).
        radius_m: Search radius in metres around the centre.
        query: Optional full-text filter passed to the API.

    Returns:
        A compact list of offers, each with id, name, min_price_chf,
        valid_from, valid_through and url. Use get_offer_details(id)
        to inspect promising candidates.

    Raises:
        httpx.HTTPStatusError: If the OpenData API responds with an
            error status (e.g. invalid API key or rate limit).
    """
    params = {
        "geo.dist": f"{latitude},{longitude},{radius_m}",
        "hitsPerPage": 50,
    }
    if query:
        params["query"] = query
    response = httpx.get(
        f"{BASE_URL}/offers", params=params, headers=HEADERS, timeout=20
    )
    response.raise_for_status()

    results = []
    for offer in response.json()["data"]:
        results.append(
            {
                "id": offer.get("identifier"),
                "name": offer.get("name"),
                "min_price_chf": (offer.get("priceSpecification") or {}).get(
                    "minPrice"
                ),
                "valid_from": offer.get("validFrom"),
                "valid_through": offer.get("validThrough"),
                "url": offer.get("url"),
            }
        )
    return results


@mcp.tool
def get_offer_details(offer_id: str) -> dict:
    """Fetch full details for one offer by its id.

    Use after search_offers to inspect promising candidates before
    ranking them.

    Args:
        offer_id: The offer's identifier as returned by search_offers.

    Returns:
        A dict with id, name, min_price_chf, valid_from, valid_through,
        url, description (truncated to ~500 characters), booking_url
        and the destination's coordinates (destination_lat/_lon).

    Raises:
        httpx.HTTPStatusError: If the OpenData API responds with an
            error status (e.g. unknown id, invalid API key).
    """
    response = httpx.get(
        f"{BASE_URL}/offers/{offer_id}",
        params={"expand": "true", "striphtml": "true"},
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()
    offer = response.json()["data"]
    geo = ((offer.get("areaServed") or {}).get("geo")) or {}
    return {
        "id": offer.get("identifier"),
        "name": offer.get("name"),
        "min_price_chf": (offer.get("priceSpecification") or {}).get(
            "minPrice"
        ),
        "valid_from": offer.get("validFrom"),
        "valid_through": offer.get("validThrough"),
        "url": offer.get("url"),
        "description": (offer.get("description") or "")[:500],
        "booking_url": offer.get("mainEntityOfPage"),
        "destination_lat": geo.get("latitude"),
        "destination_lon": geo.get("longitude"),
    }


if __name__ == "__main__":
    mcp.run()
