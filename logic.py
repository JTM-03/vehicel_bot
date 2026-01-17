import streamlit as st
from langchain_groq import ChatGroq
from datetime import date

def get_advanced_report(v_type, model, m_year, odo, district, road_env, tyre_odo, align, pressure, service, usage):
    # 1. API Key Check
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Please add your GROQ_API_KEY to Streamlit Secrets."

    # 2. Tyre Wear Predictor Logic
    tyre_km_driven = max(0, odo - tyre_odo)
    wear_factor = 1.0
    if align == "Rarely": wear_factor += 0.4
    if pressure == "Only when low": wear_factor += 0.2
    if road_env in ["Potholes/Rough", "Mountain Slopes"]: wear_factor += 0.5
    if "Electric" in v_type: wear_factor += 0.2 # EVs are heavier
    
    effective_wear = tyre_km_driven * wear_factor
    tyre_prediction = "GOOD"
    if effective_wear > 35000: tyre_prediction = "FAIR"
    if effective_wear > 50000: tyre_prediction = "DANGEROUS"

    # 3. Usage/Stagnation Check
    valid_dates = [d for d in usage['dates'] if d is not None]
    is_stagnant = False
    if len(valid_dates) >= 2:
        days_gap = (max(valid_dates) - min(valid_dates)).days
        if days_gap > 14: is_stagnant = True

    # 4. Prompt for AI (Separating Warnings and Costs)
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    prompt = f"""
    Role: Sri Lankan Automotive Diagnostic Expert (2026).
    Vehicle: {m_year} {model} ({v_type}). District: {district}.
    Odometer: {odo}km. Tyre Age: {tyre_km_driven}km. 
    Alignment Habit: {align}. Road: {road_env}.
    Stagnation (Vehicle sits idle > 14 days): {is_stagnant}.

    FORMATTING RULES:
    1. Header: "### ⚠️ Mechanical Warnings"
       - Use :red[DANGER], :orange[WARNING], :green[SAFE].
       - Explain what happens if NOT fixed (e.g., "Engine oil solidification", "Brake fade").
    2. Header: "### 💰 Estimated Repair Costs (LKR)"
       - Provide a separate list of costs in Sri Lankan Rupees.
       - Use 2026 market prices (e.g., Engine oil 18k, Tyres 35k each).
    3. EV LOGIC: If vehicle is "Electric", do NOT mention engine oil or spark plugs. Focus on Reduction Gear Oil, Battery Coolant, and 12V Health.
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"