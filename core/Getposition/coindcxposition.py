import hmac
import hashlib
import json
import time
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("Coindcx_apikey")
SECRET = os.getenv("Coindcx_apisecret")
URL = os.getenv("Coindcx_url_position")

async def get_position(symbol: str):
    """
    Async version - fast and non-blocking.
    """

    secret_bytes = SECRET.encode("utf-8")
    timestamp = int(time.time() * 1000)

    body = {
        "timestamp": timestamp,
        "page": "1",
        "size": "10",
        "pairs": symbol,
        "margin_currency_short_name": ["INR"]
    }

    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": KEY,
        "X-AUTH-SIGNATURE": signature
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(URL, data=json_body, headers=headers) as resp:
                return await resp.json()
        except Exception as e:
            return {"error": str(e)}
