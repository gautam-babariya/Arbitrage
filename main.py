from flask import Flask, request, jsonify, render_template
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import threading
from threading import Thread
import agents.agent1_watcher.watcher as agent1
from config.mongo import trading_collection
import requests
from agents.agent2_executor.executor import executor_worker
import agents.agent2_executor.executor as agent2
from dotenv import load_dotenv
from core.websocets.coin_markprice import stop_socket

load_dotenv()
backendUrl = os.getenv("backendUrl")

app = Flask(__name__)
watcher_thread = None
stop_event = threading.Event()
thread_running = False


executor_stop_event = threading.Event()

executor_thread = threading.Thread(target=executor_worker, args=(executor_stop_event,))
executor_thread.daemon = True
executor_thread.start()


@app.route("/")
def home():
    return agent1.data;
@app.route("/order_book")
def order_nook():
    return agent2.data;

@app.route("/add_symbol")
def form_page():
    return render_template("add_symbol.html")

@app.route("/add_symbol_post", methods=["POST"])
def add_symbol_post():
    symbol = request.form.get("symbol")
    target_price = request.form.get("target_price")
    stop_price = request.form.get("stop_price")
    Orderid_coindcx = request.form.get("Orderid_coindcx")
    Orderid_delta = request.form.get("Orderid_delta")

    if not symbol or not target_price or not stop_price or not Orderid_coindcx or not Orderid_delta:
        return jsonify({"error": "All fields required"}), 400

    # Convert symbol to uppercase for consistency
    symbol = symbol.upper()

    # Check if symbol already exists
    existing = trading_collection.find_one({"symbol": symbol})
    if existing:
        return jsonify({
            "error": "Symbol already exists",
            "symbol": symbol
        }), 409   # 409 = conflict (duplicate)

    # Insert into Mongo
    trading_collection.insert_one({
        "symbol": symbol,
        "target_price": float(target_price),
        "stop_price": float(stop_price),
        "Orderid_coindcx": Orderid_coindcx,
        "Orderid_delta": Orderid_delta
    })
    threading.Thread(target=restart_watcher, daemon=True).start()
    return jsonify({
        "message": "Symbol added successfully",
        "symbol": symbol
    }), 200

@app.route("/remove_symbol_post", methods=["POST"])
def remove_symbol():
    symbol = request.form.get("symbol")

    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    # Try to delete symbol
    result = trading_collection.delete_one({"symbol": symbol})

    if result.deleted_count == 0:
        return jsonify({"error": "Symbol not found"}), 404

    threading.Thread(target=restart_watcher, daemon=True).start()
    
    return jsonify({
        "message": "Symbol removed successfully",
        "symbol": symbol
    }), 200

@app.route("/stop_watcher")
def stop_watcher():
    global thread_running, watcher_thread
    stop_socket()
    if not thread_running:
        return "Watcher already stopped"

    # Tell thread to stop
    stop_event.set()
    thread_running = False

    # Wait for thread to finish safely
    if watcher_thread is not None:
        watcher_thread.join(timeout=3)
        watcher_thread = None
    return "Watcher stopped"

@app.route("/start_watcher")
def start_watcher():
    global watcher_thread, thread_running

    if thread_running:
        return "Watcher already running"

    print("▶ Starting watcher...")

    stop_event.clear()

    watcher_thread = threading.Thread(
        target=agent1.run,
        args=(stop_event,),
        daemon=True
    )
    watcher_thread.start()

    thread_running = True
    return "Worker started"

def restart_watcher():
    data = list(trading_collection.find({}, {"_id": 0}))
    try:
        if len(data) == 0:
            requests.get(f"{backendUrl}/stop_watcher")
            print("▶ Stop watcher...")
        else:
            requests.get(f"{backendUrl}/stop_watcher")
            requests.get(f"{backendUrl}/start_watcher")

    except Exception as e:
        print("❌ Error restarting watcher:", e)
        
if __name__ == "__main__":
    app.run(debug=True)

