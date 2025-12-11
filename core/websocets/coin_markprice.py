# websocket_prices.py
import socketio
import threading
import json

socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.Client(reconnection=True, reconnection_attempts=5)

symbols = []

market_prices = {}      
stop_event = threading.Event()

@sio.event
def connect():
    print("✔ Connected to CoinDCX WebSocket")
    sio.emit('join', {"channelName": "currentPrices@futures@rt"})

@sio.on("currentPrices@futures#update")
def on_message(response):
    try:
        msg = json.loads(response["data"])
        prices_dict = msg["prices"]  
        for sym in symbols:   # only DB symbols
            info = prices_dict.get(sym)   # Direct lookup, no compare all
            if info:
                if info.get("mp"):
                    market_prices[sym] = info.get("mp")
        for key in list(market_prices.keys()):
            if key not in symbols:
                del market_prices[key]
        
    except Exception as e:
        print("❌ Decode error:", e)



def start_socket(symbole_list):
    global symbols
    symbols =  list(symbole_list.keys())
    def run():
        try:
            sio.connect(socketEndpoint, transports="websocket")
            sio.wait()    # keep alive forever
        except Exception as e:
            print("❌ Socket error:", e)
        
    stop_event.clear()
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("▶ WebSocket started.")

def stop_socket():
    """Stop websocket manually (only when this is called)."""
    stop_event.set()
    try:
        sio.disconnect()
    except:
        pass
    print("🛑 WebSocket stopped.")
