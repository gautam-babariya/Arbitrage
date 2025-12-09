# mongo_config.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()

# Read value from .env
MONGO_URL = os.getenv("MONGO_URL")

# Connect MongoDB
client = MongoClient(MONGO_URL)

# Select database
db = client["Trading"]

# Select collections
trading_collection = db["Arbitrage"]
queue_collection = db["event_queue"]