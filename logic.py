import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# --- 1. SETUP KEYS ---
def get_keys():
    g_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    w_key = st.secrets.get("WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
    return g_key, w_key

def get_llm():
    g_key, _ = get_keys()
    if not g_key: return None
    # Using the stable model for 2026
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=g_key, temperature=0.3)

# --- 2. CALCULATORS (The missing function is here!) ---
def get_oil_interval(vehicle_name):
    """Asks AI for the specific oil change interval for this car"""
    llm = get_llm()
    if not llm: return 5000 

    try:
        # We force the AI to give us just a number
        prompt = f"What is the recommended oil change interval in KM for a {vehicle_name}? Output ONLY the number (e.g. 5000)."
        response = llm.invoke(prompt)
        # Extract digits only
        return int(''.join(filter(str.isdigit, response.content)))
    except:
        return 5000 # Safety fallback

# --- 3. WEATHER (More Specific) ---
def get_weather_risk(location):
    _, w_key = get_keys()
    if not w_key: return 0, "Weather Key Missing"
    
    # We ask for "Location, Country" to be more precise
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={w_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200: 
            return 0, f"Location Error: {res.get('message')}"
            
        condition = res['weather'][0]['main'].lower()
        desc = res['weather'][0]['description']
        temp = res['main']['temp']
        
        # Risk Logic
        if "rain" in condition or "storm" in condition:
            return 25, f"🌧️ Wet Roads ({desc}, {temp}°C)"
        elif "mist" in condition or "fog" in condition:
            return 15, f"🌫️ Low Visibility ({desc}, {temp}°C)"
        else:
            return 0, f"☀️ Good Conditions ({desc}, {temp}°C)"
    except:
        return 0, "Weather Unavailable"

# --- 4. THE PRO REPORT GENERATOR ---
def get_detailed_report(vehicle, odometer, last_oil, recent_repairs, weather_desc):
    llm = get_llm()
    if not llm: return "AI Error"

    prompt = f"""
    Act as a Senior Vehicle Mechanic. Analyze this vehicle:
    - Car: {vehicle}
    - Odometer: {odometer} km
    - Last Service: {last_oil} km
    - Recent Repairs Done by User: {recent_repairs}
    - Current Driving Weather: {weather_desc}

    Generate a detailed report with these exact 3 sections:
    
    SECTION 1: NEXT SERVICE
    - Calculate exactly when the next service is due (in km).
    - Is it overdue? (Yes/No).

    SECTION 2: SPARE PARTS CHECKLIST
    - List 3-4 specific parts that likely need changing at this mileage (e.g., Timing Belt, Spark Plugs, Brake Pads).
    - Do NOT suggest parts listed in 'Recent Repairs'.

    SECTION 3: WEATHER ADVICE
    - Give one specific driving tip for the current weather and this car type.
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Could not generate report: {str(e)}"