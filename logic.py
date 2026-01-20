import streamlit as st
from langchain_groq import ChatGroq
import base64

def get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, service_odo, trips):
    api_key = st.secrets.get("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    # Financial context for 2026
    vat, sscl = "18%", "2.5%"
    
    prompt = f"""
    Act as a Sri Lankan Automobile Engineer (2026).
    Vehicle: {m_year} {model} ({v_type}) in {city}, {district}.
    Odo: {odo}km. Last Service: {service_odo}km. Last Alignment: {align_odo}km.
    
    RECENT TRIP DATA:
    {trips}

    STRICT OUTPUT FORMAT:
    ### ⚠️ {district} Road & Environment Warning
    - Analyze the {trips} data against {city}'s terrain.
    - Mention specific risks (e.g., if trips show 'Mountain' in {district}, check brake wear).
    
    ### 💰 2026 Costing & Justification (LKR)
    - Provide 2026 estimates including {vat} VAT and {sscl} SSCL.
    - Justification: Explain the 'Market-Linked Markup' method due to 2026 import tariffs (up to 30%).

    ### 🛠️ Localized Service Centers
    - Suggest 2 reputable centers near {city}.
    """
    try:
        return llm.invoke(prompt).content
    except Exception as e: return f"Error: {str(e)}"

def analyze_vision_chat(image_file, user_query, vehicle_context):
    api_key = st.secrets.get("GROQ_API_KEY")
    vision_llm = ChatGroq(model="llama-3.2-11b-vision-preview", groq_api_key=api_key)
    image_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    prompt = [
        {"role": "user", "content": [
            {"type": "text", "text": f"Context: {vehicle_context}. Query: {user_query}. Analyze image for maintenance/errors. Include 2026 LKR costs with 18% VAT and 2.5% SSCL."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]}
    ]
    try:
        return vision_llm.invoke(prompt).content
    except Exception as e: return "Vision system error. Please ensure the image is clear."