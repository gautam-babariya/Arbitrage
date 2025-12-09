import aiohttp
from delta_rest_client import DeltaRestClient
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.mongo import queue_collection
load_dotenv()

Delta_baseurl = os.getenv("Delta_baseurl")
Delta_apikey = os.getenv("Delta_apikey")
Delta_apisecret = os.getenv("Delta_apisecret")

headers = {
    "Accept": "application/json"
}

delta_client = DeltaRestClient(
    base_url=Delta_baseurl,
    api_key=Delta_apikey,
    api_secret=Delta_apisecret
)

async def get_orderid(symbol: str):
    """Fetch Delta product_id using ticker symbol."""
    url = f"{Delta_baseurl}/v2/tickers/{symbol}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as res:
            data = await res.json()
            result = data.get("result", {})
            return result.get("product_id")


async def get_position(symbol: str):
    """
    Convert B-SWARMS_USDT → SWARMSUSD,
    fetch product_id, then get Delta position.
    """
    cursor = queue_collection.find(
        {"symbol": symbol},
        {"_id": 0, "Orderid_delta": 1}
    ).sort("_id", -1).limit(1)

    doc = next(cursor, None)

    leverage_delta = doc.get("Orderid_delta") if doc else None

    # Convert B-SWARMS_USDT → SWARMSUSD
    symbol = symbol.replace("B-", "")
    base, quote = symbol.split("_")
    quote = quote.replace("USDT", "USD")
    final_symbol = base + quote

    # Get product_id
    sym_id = await get_orderid(final_symbol)

    if not sym_id:
        return {"error": f"Invalid symbol or product_id not found: {final_symbol}"}

    # DeltaRestClient is NOT async, so call directly
    response = delta_client.get_position(sym_id)
    return response,sym_id,leverage_delta
