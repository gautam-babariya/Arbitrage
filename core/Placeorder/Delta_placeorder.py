from delta_rest_client import DeltaRestClient
from delta_rest_client import OrderType
import os
from dotenv import load_dotenv

load_dotenv()
Delta_baseurl = os.getenv("Delta_baseurl")
Delta_apikey = os.getenv("Delta_apikey")
Delta_apisecret = os.getenv("Delta_apisecret")

delta_client = DeltaRestClient(
    base_url=Delta_baseurl,
    api_key=Delta_apikey,
    api_secret=Delta_apisecret
)

def place_delta_order(product_id, size, side, order_type, price=None, leverage=1):
    try:
        # Set leverag
        # Convert order type to enum
        if order_type.lower() == "market_order":
            ot = OrderType.MARKET
            price = None     # market order doesn't require price
        else:
            ot = OrderType.LIMIT
            if price is None:
                return {"error": "Limit order requires limit_price"}
        
        # Build order request
        params = {
            "product_id": product_id,
            "size": size,
            "side": side,
            "order_type": ot,
        }
        
        if price is not None:
            params["limit_price"] = str(price)

        # Send to Delta Exchange API
        response = delta_client.place_order(**params)

        return response

    except Exception as e:
        return {"error": str(e)}
