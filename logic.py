import os
import streamlit as st
from langchain_groq import ChatGroq

def get_llm():
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Please add GROQ_API_KEY to your Streamlit Secrets!")
        return None
    # llama-3.3-70b is currently the most reliable free model on Groq
    return ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)

def get_detailed_report(vehicle, odometer, last_oil, repairs, district, town):
    llm = get_llm()
    if not llm: return "Config Error"

    # Precise logic for Kesbewa
    if town.lower() == "kesbewa":
        env_context = "High-traffic urban hub. Extreme engine idling risk. Inland (Low salt air risk)."
    else:
        env_context = "Standard driving zone."

    prompt = f"""
    Mechanical Analysis for {vehicle} in {town}, {district}.
    Environment: {env_context}
    Mileage: {odometer}km. Last Service: {last_oil}km.
    Repairs done: {repairs}

    Provide a professional report with:
    1. A section on 'Traffic Impact' for {town}.
    2. Next service mileage goal.
    3. List of spare parts (Filters, Pads, or Fluids) based on this mileage and area.
    """
    
    return llm.invoke(prompt).content