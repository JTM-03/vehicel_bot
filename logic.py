import os
import streamlit as st
from langchain_groq import ChatGroq
from datetime import date

def get_advanced_report(v_type, model, m_year, odo, district, road_env, tyre_odo, align, pressure, service, usage):
    # --- 1. Safety Check: API Key ---
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ **Configuration Error**: Please add `GROQ_API_KEY` to your Streamlit Secrets."

    # --- 2. Logic: Tyre Wear Prediction ---
    # We calculate wear based on mileage + neglect factors
    tyre_age_km = max(0, odo - tyre_odo)
    wear_multiplier = 1.0
    if align == "Rarely": wear_multiplier += 0.3
    if pressure == "Only when low": wear_multiplier += 0.2
    if road_env == "Potholes/Rough": wear_multiplier += 0.4
    if "Electric" in v_type: wear_multiplier += 0.2 # EVs are heavier, wearing tyres faster

    calculated_status = "Good"
    if (tyre_age_km * wear_multiplier) > 30000: calculated_status = "Fair"
    if (tyre_age_km * wear_multiplier) > 45000: calculated_status = "DANGEROUS"

    # --- 3. Logic: Usage/Stagnation Check ---
    # Safety: Only calculate if dates are not None
    stagnation_warning = False
    valid_dates = [d for d in usage['dates'] if d is not None]
    if len(valid_dates) >= 2:
        days_gap = (max(valid_dates) - min(valid_dates)).days
        if days_gap > 14: # Car not used for 2 weeks
            stagnation_warning = True

    # --- 4. AI Prompt (Strict Instructions) ---
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    # Contextual flags
    is_ev = "Electric" in v_type
    is_hilly = district in ["Kandy", "Nuwara Eliya", "Badulla"] or road_env == "Mountain Slopes"

    prompt = f"""
    Act as a Master Mechanic. Vehicle: {m_year} {model} ({v_type}). 
    Odometer: {odo}km. Location: {district}.
    
    Mechanical Data:
    - Calculated Tyre Status: {calculated_status} (Based on {tyre_age_km}km use)
    - Road Type: {road_env}
    - Stagnation (Unused > 14 days): {stagnation_warning}
    - Last Service: {service}km
    - Hilly Area: {is_hilly}

    RULES:
    1. Use :red[DANGER] for high risks, :orange[WARNING] for medium, :green[SAFE] for good.
    2. If EV: STRICTLY ignore engine oil/spark plugs. Focus on Reduction Gear Oil and Battery Coolant.
    3. Keep it simple. Bullet points only.
    4. Predict what happens if they DON'T fix it.
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"⚠️ **AI Error**: {str(e)}"