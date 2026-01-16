import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_keys():
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"], st.secrets["WEATHER_API_KEY"]
    else:
        return os.getenv("GOOGLE_API_KEY"), os.getenv("WEATHER_API_KEY")

google_key, weather_key = get_keys()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_key)

def get_oil_interval(vehicle_name):
    try:
        prompt = f"What is the recommended oil change interval in KM for a {vehicle_name}? Provide ONLY the number."
        response = llm.invoke(prompt)
        return int(''.join(filter(str.isdigit, response.content)))
    except:
        return 8000

def get_weather_risk(city):
    if not weather_key:
        return 0, "Weather Key Missing"
    
    # We use 'https' now for better compatibility
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200: # Check if city exists or key is active
            return 0, f"Wait for API Activation (Error: {res.get('message')})"
            
        main_weather = res['weather'][0]['main'].lower()
        temp = res['main']['temp']
        
        if "rain" in main_weather or "storm" in main_weather:
            return 20, f"🌧️ High Risk: Rain detected in {city} ({temp}°C)."
        else:
            return 0, f"☀️ Low Risk: Clear skies in {city} ({temp}°C)."
    except:
        return 0, "⚠️ Connection to Weather Service failed."

def get_maintenance_advice(vehicle, km_since_oil, weather_desc):
    """Asks Gemini for a specific fix-it list based on the analysis."""
    prompt = f"""
    A user is driving a {vehicle}. 
    It has been {km_since_oil}km since their last oil change.
    Current weather condition: {weather_desc}.
    
    Provide a bulleted 'Maintenance Action Plan':
    1. Tell them exactly what to check (Tires, Brakes, Oil).
    2. Give one 'Urgent' fix if the oil is overdue.
    3. Give one 'Weather Safety' tip for this specific condition.
    Keep it short and helpful.
    """
    response = llm.invoke(prompt)
    return response.content