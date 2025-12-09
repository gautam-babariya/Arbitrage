import aiohttp
import asyncio

async def fetch_orderbook(symbol: str):
    """
    Async fetch of Delta L2 orderbook for a given symbol.
    Input example: B-SWARMS_USDT
    Converts to: SWARMSUSD
    """
    
    headers = {
        'Accept': 'application/json'
    }

    # --- Convert symbol ---
    clean = symbol.replace("B-", "")
    base, quote = clean.split("_")
    quote = quote.replace("USDT", "USD")
    final_symbol = base + quote

    url = f'https://api.india.delta.exchange/v2/l2orderbook/{final_symbol}'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                data = await response.json()
                return data

        except aiohttp.ClientError as e:
            return {"error": f"Client error: {e}", "url": url}

        except aiohttp.ContentTypeError:
            # Raised if response is not JSON
            text = await response.text()
            return {"error": "Invalid JSON response", "raw": text, "url": url}
