import os
import pymongo
import streamlit as st
from dotenv import load_dotenv

# This function safely finds your connection string no matter where the app is running
def get_db_client():
    # 1. Try to get URI from Streamlit Cloud Secrets first
    if "MONGO_URI" in st.secrets:
        mongo_uri = st.secrets["MONGO_URI"]
    else:
        # 2. If not in Cloud, load from your local .env file
        load_dotenv()
        mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        st.error("Missing MONGO_URI! Please check your .env file or Streamlit Secrets.")
        return None
        
    try:
        # We add 'tlsAllowInvalidCertificates' to help Streamlit Cloud bypass SSL hurdles
        client = pymongo.MongoClient(
            mongo_uri, 
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True 
        )
        # This line forces a connection check immediately
        client.server_info() 
        return client
    except Exception as e:
        st.error(f"MongoDB Connection Error: {e}")
        return None

def save_vehicle_profile(data):
    client = get_db_client()
    if client:
        db = client["vehicle_bot_db"]
        users = db["users"]
        users.update_one(
            {"user_id": "default_user"},
            {"$set": data},
            upsert=True
        )
        return True
    return False

def get_vehicle_profile():
    client = get_db_client()
    if client:
        db = client["vehicle_bot_db"]
        return db["users"].find_one({"user_id": "default_user"})
    return None