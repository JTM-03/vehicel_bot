import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_keys():
    # Try Streamlit Secrets first, then local .env
    g_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    w_key = st.secrets.get("WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
    return g_key, w_key

def get_maintenance_advice(vehicle, km_since_oil, weather_desc):
    g_key, _ = get_keys()
    
    if not g_key:
        return "❌ Error: Google API Key is missing in Streamlit Secrets!"

    try:
        # Use 'gemini-2.0-flash' - the 2026 stable standard
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=g_key,
            temperature=0.2
        )
        
        prompt = f"Car: {vehicle}. Odometer: {km_since_oil}km since last oil change. Weather: {weather_desc}. List 3 priority maintenance tasks."
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        # This will show the REAL error (like 'Invalid Key' or 'Quota Exceeded') 
        # instead of the 'Redacted' message.
        return f"⚠️ AI Diagnostic Error: {str(e)}"

def get_weather_risk(city):
    _, w_key = get_keys()
    if not w_key:
        return 0, "Weather Key Missing in Secrets"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={w_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200:
            return 0, f"Weather API Error: {res.get('message', 'Unknown')}"
            
        condition = res['weather'][0]['main']
        temp = res['main']['temp']
        return (20, f"🌧️ Rain: {condition} ({temp}°C)") if "Rain" in condition else (0, f"☀️ Clear: {condition} ({temp}°C)")
    except:
        return 0, "Weather Service Offline"