import os
import streamlit as st
from langchain_groq import ChatGroq # NEW: Use Groq instead of Google

def get_llm():
    """Reliable LLM connection using Groq"""
    # Get the key from Streamlit secrets
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("GROQ_API_KEY is missing!")
        return None

    # We use Llama 3.3 70B - it's very smart and works great for diagnostics
    return ChatGroq(
        model="llama-3.3-70b-versatile", 
        groq_api_key=api_key,
        temperature=0.2,
        max_retries=2
    )

def get_detailed_report(vehicle, odometer, last_oil, repairs, district, town):
    llm = get_llm()
    if not llm: return "Configuration Error."

    # Keep your exact same prompt logic
    prompt = f"""
    Act as a professional Sri Lankan Automotive Engineer.
    Vehicle: {vehicle}, Mileage: {odometer}km, Location: {town}, {district}.
    Recent Repairs: {repairs}.
    
    Provide a professional maintenance report including:
    1. Environmental risks for {town}.
    2. Next service mileage.
    3. Parts to check immediately.
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"System Error: {str(e)}"