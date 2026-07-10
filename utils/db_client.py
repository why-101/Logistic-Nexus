import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# We add connectTimeoutMS and serverSelectionTimeoutMS to help with slow DNS
client = MongoClient(
    os.getenv("MONGO_URI"),
    connectTimeoutMS=30000,
    serverSelectionTimeoutMS=30000
)

db = client['Logistics'] # Ensure this matches your DB name[cite: 7]