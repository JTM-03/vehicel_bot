import streamlit as st
from database import get_db_client

st.title("🚗 Vehicle Bot: Phase 2 Test")

if st.button("Test Database Connection"):
    client = get_db_client()
    if client:
        st.success("✅ Successfully connected to MongoDB Atlas!")
        # Show existing databases to prove it works
        dbs = client.list_database_names()
        st.write("Available Databases:", dbs)
    else:
        st.error("❌ Connection Failed. Check your .env file and MongoDB Network Access.")