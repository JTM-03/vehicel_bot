import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load keys
load_dotenv()

def get_keys():
    """Helper to get keys from either Secrets or .env"""
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"], st.secrets["WEATHER_API_KEY"]
    else:
        return os.getenv("GOOGLE_API_KEY"), os.getenv("WEATHER_API_KEY")

google_key, weather_key = get_keys()

# Setup Gemini
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_key)

def get_oil_interval(vehicle_name):
    """Asks Gemini for the oil change interval."""
    try:
        prompt = f"What is the recommended oil change interval in kilometers (KM) for a {vehicle_name}? Provide ONLY the number, no text."
        response = llm.invoke(prompt)
        # Extract numbers only (e.g., "10000")
        return int(''.join(filter(str.isdigit, response.content)))
    except:
        return 8000  # Default fallback

def get_weather_risk(city):
    """Fetches weather and returns a risk score (0-20)"""
    if not weather_key:
        return 0, "Weather API Key Missing"
        
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}&units=metric"
    try:
        res = requests.get(url).json()
        main_weather = res['weather'][0]['main'].lower()
        
        if "rain" in main_weather or "storm" in main_weather:
            return 20, "🌧️ High (Wet/Slippery Roads)"
        elif "cloud" in main_weather:
            return 5, "☁️ Moderate (Cloudy)"
        else:
            return 0, "☀️ Low (Clear Skies)"
    except:
        return 0, "⚠️ Weather Data Unavailable"