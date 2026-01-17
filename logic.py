import os
import time
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted

def get_environment_context(district, town):
    """
    Logical Brain: Maps geography to mechanical risks.
    Kesbewa is specifically handled as Urban/Traffic.
    """
    town_lower = town.lower().strip()
    
    # 1. MOUNTAIN LOGIC
    mountains = ["nuwara eliya", "kandy", "badulla", "bandarawela"]
    
    # 2. COASTAL LOGIC (Kesbewa is EXCLUDED here)
    coastal_towns = ["galle", "matara", "negombo", "hikkaduwa", "mount lavinia", "panadura"]
    
    # 3. URBAN/TRAFFIC LOGIC (Kesbewa is INCLUDED here)
    urban_towns = ["colombo", "kesbewa", "piliyandala", "maharagama", "nugegoda", "kaduwela"]

    context = []
    
    if town_lower in mountains or district.lower() in ["nuwara eliya", "kandy"]:
        context.append("⚠️ MOUNTAIN WARNING: Steep terrain detected. Brakes wear 40% faster. Transmission fluid needs frequent checks.")
    
    if town_lower in coastal_towns:
        context.append("🌊 COASTAL WARNING: High salt air. Significant risk of chassis decay. Recommend anti-rust undercoating.")
        
    if town_lower in urban_towns or town_lower == "kesbewa":
        context.append("🚦 URBAN TRAFFIC: Kesbewa/Colombo area. High engine idling. Oil life is shorter than mileage suggests. Check air filters for dust.")
        
    return " ".join(context) if context else "Standard driving conditions."

def get_detailed_report(vehicle, odometer, last_oil, repairs, district, town):
    g_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not g_key: return "API Key not found in Secrets."

    # Using 2.0-flash for 2026 stability
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=g_key)
    except:
        # Fallback if 2.0 is not available in your region yet
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=g_key)

    env_logic = get_environment_context(district, town)
    
    prompt = f"""
    Act as a professional Sri Lankan Automotive Engineer.
    Vehicle: {vehicle}
    Odometer: {odometer} km
    Location: {town}, {district}
    Environmental Logic: {env_logic}
    
    Based on the Environmental Logic above, provide:
    1. A 'Logical Warning' section explaining how the {town} environment specifically affects this {vehicle}.
    2. A maintenance schedule for the next 6 months.
    3. Essential parts to inspect (Brakes, Chassis, or Filters) based on the specific location risk.
    """

    # Retry mechanism for 429 Errors
    for attempt in range(3):
        try:
            return llm.invoke(prompt).content
        except ResourceExhausted:
            time.sleep(5)
        except Exception as e:
            return f"Model Error: {str(e)}"
    
    return "The system is currently overloaded. Please try again in 1 minute."