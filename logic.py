import streamlit as st
from langchain_groq import ChatGroq
from datetime import date

def get_advanced_report(v_type, model, m_year, odo, district, tyre_odo, align_km, pressure, service, trips):
    # 1. API Key Check
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Configuration Error: GROQ_API_KEY missing."

    # 2. Road Severity Calculation
    road_weights = {
        "Carpeted": 1.0, "City Traffic": 1.3, 
        "Potholes/Rough": 1.7, "Mountain Slopes": 1.9, "Slippery/Muddy": 1.6
    }
    
    total_trip_impact = 0
    for trip in trips:
        # Determine the harshest road type in the selection
        weight = max([road_weights.get(r, 1.0) for r in trip['roads']]) if trip['roads'] else 1.0
        total_trip_impact += trip['km'] * weight

    # 3. Tyre Wear Prediction (KM-based Alignment Logic)
    tyre_age_actual = odo - tyre_odo
    
    # Alignment Penalty: Base is 5000km. If they wait longer, wear increases.
    alignment_penalty = 1.0
    if align_km > 6000:
        alignment_penalty += (align_km / 10000) # Gradual increase in wear
    
    pressure_penalty = 1.3 if pressure == "Only when low" else 1.0
    ev_penalty = 1.2 if "Electric" in v_type else 1.0 # Heavier curb weight
    
    effective_wear = tyre_age_actual * alignment_penalty * pressure_penalty * ev_penalty

    # 4. Stagnation Check
    valid_dates = sorted([t['date'] for t in trips if t['date'] is not None])
    stagnation_risk = False
    if len(valid_dates) >= 2:
        for i in range(len(valid_dates)-1):
            if (valid_dates[i+1] - valid_dates[i]).days > 14:
                stagnation_risk = True

    # 5. LLM Diagnostic
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    prompt = f"""
    Act as a Master Mechanic. Vehicle: {m_year} {model} ({v_type}). District: {district}.
    Diagnostic Data:
    - Odometer: {odo}km.
    - Tyre Age: {tyre_age_actual}km. Alignment frequency: every {align_km}km.
    - Effective Tyre Wear: {effective_wear:.0f}km.
    - Road Severity (Max Weight): {max([road_weights.get(r, 1.0) for t in trips for r in t['roads']] if any(t['roads'] for t in trips) else [1.0])}.
    - Stagnation Risk: {stagnation_risk}.

    STRICT FORMAT:
    ### ⚠️ Mechanical Warnings
    - Analyze dangers based on the terrain and vehicle type ({v_type}).
    - Be concise. Use :red[DANGER], :orange[WARNING], :green[SAFE].
    - Explain 'Failure Consequence' (what happens if ignored).

    ### 💰 Estimated Repair Costs (LKR)
    - List current 2026 Sri Lankan market prices for parts and labor.
    - Separate by line items.
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"System Error: {str(e)}"