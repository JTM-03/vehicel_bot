import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_api_keys():
    # Priority 1: Streamlit Secrets (Production)
    if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"], st.secrets.get("WEATHER_API_KEY")
    # Priority 2: .env file (Local Development)
    return os.getenv("GOOGLE_API_KEY"), os.getenv("WEATHER_API_KEY")

def get_llm():
    g_key, _ = get_api_keys()
    if not g_key:
        st.error("🔑 Google API Key is missing! Check your Streamlit Secrets.")
        return None
    
    # Using gemini-2.0-flash for 2026 stability
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        google_api_key=g_key,
        temperature=0.3
    )

def get_maintenance_advice(vehicle, km_since_oil, weather_desc):
    llm = get_llm()
    if not llm: return "AI Configuration Error."

    prompt = f"Car: {vehicle}. Odometer: {km_since_oil}km since last oil change. Weather: {weather_desc}. List 3 priority maintenance tasks."
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"