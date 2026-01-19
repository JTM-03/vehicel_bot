import streamlit as st
from langchain_groq import ChatGroq
from datetime import date

def get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_km, pressure, service, trips):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Configuration Error: GROQ_API_KEY missing."

    # 1. Environmental & Terrain Weights
    # Different districts have different "Environmental Stress"
    env_stress = {
        "Colombo": 1.2, "Gampaha": 1.2, "Kalutara": 1.3, # Traffic/Humidity
        "Kandy": 1.5, "Nuwara Eliya": 1.8, "Badulla": 1.7, "Matale": 1.4, # Mountains
        "Galle": 1.4, "Matara": 1.3, "Hambantota": 1.3, "Jaffna": 1.5, # Coastal Salt
        "Anuradhapura": 1.4, "Polonnaruwa": 1.4, "Trincomalee": 1.4 # Heat/Dust
    }
    stress_factor = env_stress.get(district, 1.0)

    # 2. Tyre & Mechanical Wear Calculation
    tyre_age = max(0, odo - tyre_odo)
    # Alignment penalty: Standard is every 5000km.
    align_penalty = 1.0 + (max(0, align_km - 5000) / 10000)
    effective_wear = tyre_age * stress_factor * align_penalty

    # 3. AI Prompt: Localized Diagnostic + 2026 Costing
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    prompt = f"""
    Act as a Sri Lankan Automobile Engineer (2026). 
    Vehicle: {m_year} {model} ({v_type}). 
    Location: {city}, {district}.
    
    ENVIRONMENTAL CONTEXT:
    - Local Stress Factor: {stress_factor} (e.g., 1.8 = Mountain/Steep, 1.4 = Coastal/Salt).
    - Calculated Tyre Wear: {effective_wear:.0f}km effective use.

    STRICT OUTPUT STRUCTURE:
    ### ⚠️ Localized Mechanical Warnings
    - Address city-specific issues (e.g., if near coast, mention rust/corrosion. If Central, mention brake fade/suspension).
    - Include specific checks for {v_type} (e.g., Three-wheeler grease points or EV battery cooling).

    ### 💰 2026 Costing & Justification
    - List repair costs in LKR.
    - JUSTIFICATION: Explain that costs include 18% VAT, 2.5% SSCL, and 2026 import duties (up to 30%). 
    - Use the 'Market Markup' method (reflecting spare part scarcity).

    ### 🛠️ Suggested Service Centers Near {city}
    - Suggest 2-3 reputable service centers (e.g., Mag City, Sterling, AA Ceylon, or specialized local garages like LOLC Motors).
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"System Error: {str(e)}"