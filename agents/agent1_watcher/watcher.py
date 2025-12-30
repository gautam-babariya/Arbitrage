import time
import sys
import os
import threading
trigger_lock = threading.Lock()
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.mongo import trading_collection
from core.websocets.coin_markprice import start_socket,stop_socket,market_prices
from core.event_queue import enqueue

stop_event = None

data = {}
def check_data():
    # Fetch all documents
    data = list(trading_collection.find({}, {"_id": 0}))

    # If no data exist → return False
    if len(data) == 0:
        return False

    result = {}

    for item in data:
        symbol = item["symbol"]
        result[symbol] = {
            "target_price": item["target_price"],
            "stop_price": item["stop_price"],
            "Orderid_delta" : item["Orderid_delta"],
            "Orderid_coindcx" : item["Orderid_coindcx"]
        }
    return result
        
def run(event):
    symbole_list = check_data()
    if not symbole_list:
        print("Stopping watcher...")
        stop_socket()
        return 
    start_socket(symbole_list)
    
    while not event.is_set():
        symbols =  list(symbole_list.keys())
        for sym in symbols:
            if sym in market_prices:
                current_price = market_prices[sym]
                target_price = symbole_list[sym]["target_price"]
                stop_price = symbole_list[sym]["stop_price"]
                # print(f"Checking {sym}: Current = {current_price}, Target = {target_price}, Stop = {stop_price}")
                data[sym] = f"Checking {sym}: Current = {current_price}, Target = {target_price}, Stop = {stop_price}"
                if current_price >= target_price or current_price <= stop_price:
                        Orderid_delta = symbole_list[sym]["Orderid_delta"]
                        Orderid_coindcx = symbole_list[sym]["Orderid_coindcx"]
                        
                        enqueue(sym,Orderid_delta,Orderid_coindcx)
                        
                        trading_collection.delete_one({"symbol": sym})
                        del symbole_list[sym]
                        del data[sym]
        # for datu in data.values():
        #     print(datu)
        time.sleep(1) 
