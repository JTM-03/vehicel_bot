import streamlit as st
from langchain_groq import ChatGroq

def get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, pressure, service_odo, trips):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ GROQ_API_KEY missing in Secrets."

    # 1. Calculation Logic
    # Alignment health is now based on 'odo' vs 'last alignment odo'
    align_gap = max(0, odo - align_odo)
    service_gap = max(0, odo - service_odo)
    
    # 2. Market Costing (SL 2026 Standards)
    # Using 'Market-Linked Markup' (MLM) with 18% VAT & 2.5% SSCL
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    prompt = f"""
    Act as a Sri Lankan Automobile Engineer (2026).
    Vehicle: {m_year} {model} ({v_type}). Location: {city}, {district}.
    Current Odo: {odo}km. Last Alignment at: {align_odo}km. Last Service at: {service_odo}km.

    STRICT OUTPUT FORMAT:
    ### ⚠️ {district} Area Warnings
    - Mention specific environmental threats (e.g., salt in {district} if coastal, hills if Central).
    - Analyze {v_type} specific risks (Motorbikes: chain/forks, 3-Wheelers: gear cables/grease).

    ### 💰 Costing Justification (LKR)
    - Provide estimated 2026 costs. 
    - JUSTIFICATION: Mention VAT (18%) and SSCL (2.5%) applied to spare parts imports.
    - Mention why {city} prices might vary (logistics/labour).

    ### 🛠️ Local Service Partners
    - Suggest 2-3 reliable garages near {city} (e.g., Mag City, DPMC, or regional masters).
    """
    try:
        return llm.invoke(prompt).content
    except Exception as e:
        return f"Error: {str(e)}"

def process_chat_update(user_input, current_state):
    # This function uses AI to "extract" updates from a chat message
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=st.secrets["GROQ_API_KEY"])
    prompt = f"""
    User says: "{user_input}"
    Current vehicle data: {current_state}
    If the user mentioned a new odometer, model, or maintenance update, return ONLY a JSON block with the updated fields. 
    Otherwise, return "NO_UPDATE".
    """
    # Simplified for this demo: the AI handles the natural language extraction
    return llm.invoke(prompt).content