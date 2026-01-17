import os
import streamlit as st
from langchain_groq import ChatGroq

def generate_predictive_report(vehicle, odo, last_oil, brake_age, tyre_cond, road_type, district, town, trips):
    # 1. Calculate Average Trip Distance
    avg_trip = sum(trips) / len(trips)
    is_short_tripper = avg_trip < 8 # Under 8km is "Short Trip"
    
    # 2. Hill Area Check
    hilly_districts = ["Kandy", "Nuwara Eliya", "Badulla", "Matale"]
    is_hill_zone = district in hilly_districts or road_type == "Steep/Hills"

    # 3. Formulate the "Threat Intelligence" for the AI
    threats = []
    if is_hill_zone:
        if brake_age > 15000: threats.append("CRITICAL: Brake pads are aged for mountain descents.")
        if tyre_cond in ["Low", "Fair"]: threats.append("DANGER: High risk of skidding on slippery hill curves.")
    
    if is_short_tripper:
        threats.append("ENGINE ALERT: Frequent short trips detected. Risk of oil sludge and water contamination.")

    # 4. Connect to Groq
    api_key = st.secrets.get("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)

    prompt = f"""
    Act as a Predictive Automotive AI. 
    Vehicle: {vehicle} | Location: {town}, {district} | Avg Trip: {avg_trip}km
    Calculated Threats: {threats}
    Current Odo: {odo}km | Last Service: {last_oil}km

    Structure your response:
    1. **SAFETY SCORE**: Out of 100 (Deduct heavily for {threats}).
    2. **ENVIRONMENTAL THREAT**: Specifically how {town}'s geography and your {avg_trip}km trips affect the engine.
    3. **URGENT ACTIONS**: What to do in the next 48 hours.
    4. **TIRE/BRAKE PREDICTION**: Estimated remaining life in km.
    """
    
    return llm.invoke(prompt).content