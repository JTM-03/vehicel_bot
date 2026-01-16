import os
import time
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted

# --- 1. SMART CACHING ---
@st.cache_data(ttl=3600) # Remembers results for 1 hour to save API quota
def get_oil_interval(vehicle_name):
    return 5000 # Standard for SL conditions

def get_environment_context(district, town):
    """Refined logic: Kesbewa is inland/urban, not coastal."""
    mountains = ["Nuwara Eliya", "Kandy", "Badulla"]
    coastal_towns = ["Galle", "Matara", "Negombo", "Hikkaduwa", "Trincomalee"]
    urban_hubs = ["Colombo", "Kesbewa", "Piliyandala", "Maharagama", "Kottawa"]

    context = []
    if district in mountains:
        context.append("⛰️ MOUNTAIN: High brake & transmission stress.")
    if town in coastal_towns:
        context.append("🌊 COASTAL: High salt air; check for undercarriage rust.")
    if town in urban_hubs or district == "Colombo":
        context.append("🚦 URBAN TRAFFIC: High idling; oil degrades faster than mileage shows.")
    
    return " ".join(context) if context else "Standard Driving Conditions."

# --- 2. RELIABLE AI CALL ---
def get_detailed_report(vehicle, odometer, last_oil, repairs, district, town):
    g_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not g_key: return "Error: No API Key found."

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=g_key)
    env_logic = get_environment_context(district, town)
    
    prompt = f"""
    Act as an expert SL Mechanic. 
    Vehicle: {vehicle}, Odo: {odometer}km, Last Service: {last_oil}km.
    Location: {town}, {district}. Environment: {env_logic}.
    Recent Repairs: {repairs}.

    Provide a 3-section report:
    1. CRITICAL CHECKS: (Address {env_logic} specifically).
    2. NEXT SERVICE: Exact mileage for next oil/filter change.
    3. SPARE PARTS: List 3 parts likely needing replacement based on mileage.
    """

    for _ in range(3): # Retry 3 times if busy
        try:
            return llm.invoke(prompt).content
        except ResourceExhausted:
            time.sleep(5)
    return "⚠️ System busy. Please try again in 30 seconds."