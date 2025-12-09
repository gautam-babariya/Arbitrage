import aiohttp

async def fetch_orderbook(instrument: str):
    """
    Async fetch of CoinDCX futures orderbook.
    """
    url = f'https://public.coindcx.com/market_data/v3/orderbook/{instrument}-futures/50'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as res:
                return await res.json()
        except Exception as e:
            text = await res.text() if 'res' in locals() else None
            return {"error": str(e), "raw": text}
