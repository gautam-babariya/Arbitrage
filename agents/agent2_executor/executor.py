import threading
import asyncio
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from core.event_queue import dequeue, mark_done
from core.Getposition.coindcxposition import get_position as get_coindcx_position
from core.Getposition.deltaposition import get_position as get_delta_position
from core.Orderbook.orderbook_coindcx import fetch_orderbook as get_coindcx_orderbook
from core.Orderbook.orderbook_delta import fetch_orderbook as get_delta_orderbook
from core.Placeorder.Coindcx_placeorder import place_dcx_order 
from core.Placeorder.Delta_placeorder import place_delta_order 

data = {
    "demo":"gautam"
}
def start_executor_thread(event):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_order_executor(event))

def executor_worker(stop_event):
    print("⚡ MongoDB Executor Worker running...")

    while not stop_event.is_set():

        event = dequeue()   # get next pending event from Mongo
        if not event:
            time.sleep(1)
            continue

        symbol = event["symbol"]

        print(f"🚀 Starting executor thread for {symbol}")

        # Run executor thread
        t = threading.Thread(
            target=start_executor_thread,
            args=(event,)
        )
        t.daemon = True
        t.start()

        # do NOT block; let thread process
        time.sleep(0.2)

    print("🛑 Executor worker stopped")
    
async def run_order_executor(event):
    symbol = event["symbol"]
    event_id = event["_id"]

    try:
        coindcx_position = await get_coindcx_position(symbol)
        delta_position,sym_id,leverage = await get_delta_position(symbol)
        # coindcx_orderbook = await get_coindcx_orderbook(symbol)
        # delta_orderbook = await get_delta_orderbook(symbol)
    
        coindcx_qty = coindcx_position[0].get("active_pos",0)
        coindcx_leverage = coindcx_position[0].get("leverage",0)
        if isinstance(coindcx_qty, set):
            coindcx_qty = list(coindcx_qty)[0] if coindcx_qty else 0
        if isinstance(coindcx_leverage, set):
            coindcx_leverage = list(coindcx_leverage)[0] if coindcx_leverage else 0
        
        coindcx_side = "none"
        if coindcx_qty<0:
            coindcx_side = "buy"
        elif coindcx_qty>0:
            coindcx_side = "sell"
        coindcx_qty = abs(coindcx_qty)
        delta_size = delta_position.get("size")
        delta_side = "none"
        if delta_size<0:
            delta_side = "buy"
        elif delta_size>0:
            delta_side = "sell"
        delta_size = abs(delta_size)
        delta_args = (sym_id, delta_size, delta_side, "market_order", 0.01)
        dcx_args = (coindcx_side, symbol, "market_order", 0.01, coindcx_qty, coindcx_leverage)
        data["coindcx_arg"] = dcx_args
        data["delta_arg"] = delta_args
        delta_task = asyncio.to_thread(place_delta_order, *delta_args)
        dcx_task = asyncio.to_thread(place_dcx_order, *dcx_args)

        delta_result, dcx_result = await asyncio.gather(delta_task,dcx_task)

        data["coindcx_order"] = dcx_result
        data["delta_order"] = delta_result
        print(data)
        
        
    except Exception as e:
        print(f"❌ Order failed for {symbol}: {e}")

    mark_done(event_id)
    print(f"🔴 Executor completed for {symbol}, event closed")