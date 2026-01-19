import streamlit as st
from langchain_groq import ChatGroq
import base64
from datetime import datetime

# Initialize the LLM
def get_llm(model_name="llama-3.3-70b-versatile"):
    return ChatGroq(model=model_name, groq_api_key=st.secrets["GROQ_API_KEY"])

def get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, pressure, service_odo, trips):
    llm = get_llm()
    
    prompt = f"""
    Act as a Sri Lankan Automobile Engineer (2026). 
    Vehicle: {m_year} {model} ({v_type}). Location: {city}, {district}.
    Odo: {odo}km. Maintenance: Last Service {service_odo}km, Last Alignment {align_odo}km.

    STRICT OUTPUT STRUCTURE:
    ### ⚠️ {district} Environmental Warning
    - Focus on {city} specific conditions (e.g. salinity, steepness, dust).
    ### 💰 2026 Pricing (LKR)
    - List repair estimates including 18% VAT and 2.5% SSCL.
    - Justify costs using the 'Market-Linked Markup' method for imported parts.
    ### 🛠️ Recommended Local Centers
    - Suggest 2 centers near {city}.
    """
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e: return f"Error: {e}"

def analyze_photo_and_chat(image_file, user_query, vehicle_context):
    vision_llm = get_llm("llama-3.2-11b-vision-preview")
    image_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    prompt = [
        {"role": "user", "content": [
            {"type": "text", "text": f"Context: {vehicle_context}. User Question: {user_query}. Analyze the image for errors/maintenance needs. Provide 2026 LKR costs (inc. 18% VAT)."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]}
    ]
    try:
        return vision_llm.invoke(prompt).content
    except Exception as e: return "I couldn't analyze the image. Please ensure it's clear."