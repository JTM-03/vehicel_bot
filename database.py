import os
import pymongo
from dotenv import load_dotenv

# Load keys from the .env file
load_dotenv()

def get_db_client():
    """Establish connection to MongoDB Atlas."""
    mongo_uri = os.getenv("MONGO_URI")
    try:
        # Use a 5-second timeout so it doesn't hang forever if the password is wrong
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Check if the connection is successful
        client.server_info() 
        return client
    except Exception as e:
        print(f"Error: Could not connect to MongoDB. {e}")
        return None

def save_vehicle_profile(data):
    """Save or update the vehicle info in the 'users' collection."""
    client = get_db_client()
    if client:
        db = client["vehicle_bot_db"]
        users = db["users"]
        # We use update_one with upsert=True to either create or update the profile
        users.update_one(
            {"user_id": "default_user"}, # For now, we use a single user ID
            {"$set": data},
            upsert=True
        )
        return True
    return False

def get_vehicle_profile():
    """Retrieve the vehicle info from the database."""
    client = get_db_client()
    if client:
        db = client["vehicle_bot_db"]
        return db["users"].find_one({"user_id": "default_user"})
    return None