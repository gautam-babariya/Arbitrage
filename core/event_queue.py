# event_queue.py
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.mongo import queue_collection

def enqueue(symbol,Orderid_delta,Orderid_coindcx):
    """Insert new event for Agent2"""
    queue_collection.insert_one({
        "symbol": symbol,
        "Orderid_delta": Orderid_delta,
        "Orderid_coindcx": Orderid_coindcx,
        "status": "pending",
        "timestamp": int(time.time())
    })

    print(f"➡ Event stored for: {symbol}")

def dequeue():
    """Fetch next pending event and mark it processing"""
    event = queue_collection.find_one_and_update(
        {"status": "pending"},
        {"$set": {"status": "processing"}},
        sort=[("timestamp", 1)]
    )

    return event


def mark_done(event_id):
    """Mark event done after Agent2 completes work"""
    queue_collection.update_one(
        {"_id": event_id},
        {"$set": {"status": "done"}}
    )
