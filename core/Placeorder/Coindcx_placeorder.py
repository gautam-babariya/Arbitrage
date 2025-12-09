import hmac
import hashlib
import base64
import json
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def place_dcx_order(side,pair,order_type,price,total_quantity,leverage):
    api_key = os.getenv("Coindcx_apikey")
    api_secret = os.getenv("Coindcx_apisecret")
    
    secret_bytes = bytes(api_secret, encoding='utf-8')

    # Generating a timestamp
    timeStamp = int(round(time.time() * 1000))

    # Request body
    body = {
        "timestamp": timeStamp,
        "order": {
            "side": side,
            "pair": pair,
            "order_type": order_type,
            "price": price,
            "stop_price": price,
            "total_quantity": total_quantity,
            "margin_currency_short_name": "INR",
            "leverage": leverage,
            "notification": "no_notification",
            "time_in_force": "good_till_cancel",
            "hidden": False,
            "post_only": False,
        }
    }

    json_body = json.dumps(body, separators=(',', ':'))

    # Generate signature
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = os.getenv("Coindcx_url_order")

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': api_key,
        'X-AUTH-SIGNATURE': signature
    }

    # Send request
    response = requests.post(url, data=json_body, headers=headers)

    try:
        return response.json()
    except:
        return {"error": "Invalid Response", "raw": response.text}