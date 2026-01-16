import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# --- 1. SETUP KEYS & AI ---
def get_keys():
    """Helper to safely get keys from Secrets or .env"""
    g_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    w_key = st.secrets.get("WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
    return g_key, w_key

def get_llm():
    """Creates the AI connection safely"""
    g_key, _ = get_keys()
    if not g_key:
        return None
    # using gemini-2.0-flash for stability
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        google_api_key=g_key,
        temperature=0.2
    )

# --- 2. THE MISSING FUNCTION (RESTORED) ---
def get_oil_interval(vehicle_name):
    """Asks AI for the oil change km number"""
    llm = get_llm()
    if not llm: return 8000 # Default if AI is broken

    try:
        prompt = f"What is the recommended oil change interval in kilometers (KM) for a {vehicle_name}? Provide ONLY the number, no text."
        response = llm.invoke(prompt)
        # Clean the answer to get just numbers (e.g. "10000")
        return int(''.join(filter(str.isdigit, response.content)))
    except:
        return 8000 # Safety fallback

# --- 3. WEATHER FUNCTION ---
def get_weather_risk(city):
    _, w_key = get_keys()
    if not w_key:
        return 0, "Weather Key Missing"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={w_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200: 
            return 0, f"Weather Error: {res.get('message')}"
            
        condition = res['weather'][0]['main'].lower()
        temp = res['main']['temp']
        
        if "rain" in condition or "storm" in condition:
            return 20, f"🌧️ Rain detected ({temp}°C)"
        else:
            return 0, f"☀️ Clear skies ({temp}°C)"
    except:
        return 0, "Weather Service Offline"

# --- 4. MAINTENANCE ADVICE FUNCTION ---
def get_maintenance_advice(vehicle, km_since_oil, weather_desc):
    llm = get_llm()
    if not llm: return "AI Config Error: Check API Key."

    prompt = f"""
    Car: {vehicle}. 
    Odometer since last oil change: {km_since_oil}km. 
    Current Weather: {weather_desc}.
    
    Provide a checklist:
    1. One specific maintenance check for this car model.
    2. One safety tip for this specific weather.
    3. Is the oil change overdue? (Yes/No).
    """
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"