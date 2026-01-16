import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted

load_dotenv()

# --- 1. SETUP & RETRY LOGIC ---
def get_keys():
    g_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    w_key = st.secrets.get("WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
    return g_key, w_key

def get_llm():
    g_key, _ = get_keys()
    if not g_key: return None
    # Switched to 1.5-flash for speed/cost (2.0 is heavy on quotas)
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=g_key, temperature=0.3)

def safe_invoke_ai(prompt):
    """Retries the AI call if it hits a 429 Limit"""
    llm = get_llm()
    if not llm: return "AI Key Error"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            return response.content
        except ResourceExhausted:
            st.toast(f"⚠️ High traffic. Retrying in 10s... (Attempt {attempt+1}/{max_retries})")
            time.sleep(10) # Wait 10 seconds before trying again
        except Exception as e:
            return f"Error: {str(e)}"
    return "⚠️ Server is too busy. Please wait 1 minute and try again."

# --- 2. ENVIRONMENTAL LOGIC (The "Smart" Part) ---
def get_environment_context(district):
    """Maps Sri Lankan districts to logical mechanical risks"""
    
    # MOUNTAIN LOGIC
    mountains = ["Nuwara Eliya", "Kandy", "Badulla", "Ratnapura", "Matale"]
    # COASTAL LOGIC
    coastal = ["Galle", "Matara", "Colombo", "Gampaha", "Kalutara", "Trincomalee", "Batticaloa", "Jaffna", "Hambantota", "Puttalam"]
    # URBAN LOGIC
    urban = ["Colombo", "Gampaha", "Kandy"]

    context = []
    
    if district in mountains:
        context.append("MOUNTAINOUS TERRAIN: High stress on Brakes, Transmission, and Cooling System.")
    
    if district in coastal:
        context.append("COASTAL AREA: High Salinity Air. Extreme risk of Body Rust and Undercarriage Corrosion.")
        
    if district in urban:
        context.append("HEAVY TRAFFIC ZONE: High engine idle time. Oil degrades faster than mileage suggests.")
        
    return " ".join(context) if context else "Standard Driving Conditions."

# --- 3. WEATHER ---
def get_weather_risk(location):
    _, w_key = get_keys()
    if not w_key: return 0, "Weather Key Missing"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location},LK&appid={w_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200: return 0, "Weather Unavailable"
            
        condition = res['weather'][0]['main'].lower()
        desc = res['weather'][0]['description']
        temp = res['main']['temp']
        
        if "rain" in condition or "storm" in condition:
            return 25, f"🌧️ Wet ({desc}, {temp}°C)"
        else:
            return 0, f"☀️ Clear ({desc}, {temp}°C)"
    except:
        return 0, "Offline"

# --- 4. THE PRO REPORT ---
def get_detailed_report(vehicle, odometer, last_oil, repairs, weather, district):
    
    # Get the environmental logic
    env_logic = get_environment_context(district)
    
    prompt = f"""
    Act as a Senior Mechanic in Sri Lanka. 
    
    VEHICLE: {vehicle}
    ODOMETER: {odometer} km
    LAST SERVICE: {last_oil} km
    LOCATION: {district}
    ENVIRONMENT CONTEXT: {env_logic} (IMPORTANT: Use this to adjust advice)
    RECENT REPAIRS: {repairs}
    WEATHER: {weather}

    Generate a 3-part report. Be very specific to the Environment Context.
    
    1. URGENT ATTENTION
    - Based on the location ({district}), what specific part fails first? (e.g. if Coastal, check Rust; if Mountain, check Brakes).
    - Is the oil change due? (Calculate based on standard 5000km interval).

    2. SPARE PARTS WATCHLIST
    - List 3 parts to buy soon.
    
    3. DRIVING ADVICE
    - One tip for driving in {district} right now given the weather.
    """
    
    return safe_invoke_ai(prompt)

def get_oil_interval(vehicle_name):
    # Simplified to save tokens/errors
    return 5000