"""
Initializes a connection to the MongoDB Atlas 'chatbots' database, 
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client["chatbots"]  # Use the database named "chatbots"
    users_collection = db["login"]  # Use the collection titled "login"

    # Create unique index on username and email if they don't exist
    users_collection.create_index("username", unique=True)
    users_collection.create_index("email", unique=True)

    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
