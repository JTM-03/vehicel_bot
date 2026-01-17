import streamlit as st
from langchain_groq import ChatGroq
from datetime import date

def get_advanced_report(v_type, model, m_year, odo, district, tyre_odo, align, pressure, service, trips):
    # 1. API Key Check
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Please add your GROQ_API_KEY to Streamlit Secrets."

    # 2. Advanced Wear & Severity Logic
    road_weights = {
        "Carpeted": 1.0, "City Traffic": 1.2, 
        "Potholes/Rough": 1.6, "Mountain Slopes": 1.8, "Slippery/Muddy": 1.5
    }
    
    total_effective_km = 0
    max_severity = 1.0
    
    for trip in trips:
        # Get highest weight from selected road types for this trip
        trip_weight = max([road_weights.get(r, 1.0) for r in trip['roads']]) if trip['roads'] else 1.0
        total_effective_km += trip['km'] * trip_weight
        if trip_weight > max_severity: max_severity = trip_weight

    # Tyre Wear Prediction (Adjusted for 2026 standards)
    tyre_life_km = odo - tyre_odo
    # Factor in maintenance habits
    habit_penalty = 1.0
    if align == "Rarely": habit_penalty += 0.3
    if pressure == "Only when low": habit_penalty += 0.2
    
    effective_wear = (tyre_life_km + total_effective_km) * habit_penalty

    # 3. Stagnation Audit (Checking gaps between the 3 trips)
    dates = sorted([t['date'] for t in trips if t['date'] is not None])
    stagnation_risk = False
    if len(dates) >= 2:
        for i in range(len(dates)-1):
            if (dates[i+1] - dates[i]).days > 14:
                stagnation_risk = True

    # 4. AI Prompt (Refined for terrain threats and cost separation)
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    prompt = f"""
    Role: Sri Lankan Automotive Diagnostic Expert (2026).
    Vehicle: {m_year} {model} ({v_type}) in {district}.
    Recent History: 3 Trips with mixed roads (Max Severity: {max_severity}).
    Stagnation Risk (>14 days idle): {stagnation_risk}.
    Effective Tyre Wear: {effective_wear}km.

    STRICT OUTPUT FORMAT:
    ### ⚠️ Mechanical Warnings
    - Analyze terrain-specific threats (e.g., Brake glaze from mountain slopes, suspension stress from potholes).
    - Identify risks for {v_type}. (If EV: Check Reduction Gear & Battery Thermal. If ICE: Check Oil Viscosity).
    - Mention "Stagnation Damage" if stagnation_risk is True.

    ### 💰 Estimated Repair Costs (LKR)
    - List 2026 market prices for Sri Lanka.
    - Examples: Semi-Synthetic Oil (12k-15k), EVs Service (10k-25k), Tyres (30k-55k per unit).
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"