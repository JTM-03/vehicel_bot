import streamlit as st
import database as db
import logic

st.set_page_config(page_title="Vehicle Safety Bot", layout="wide")
st.title("🚗 Vehicle Safety Bot")

# --- STEP 1: VEHICLE PROFILE ---
st.header("1. Vehicle Profile")
col1, col2 = st.columns(2)

with col1:
    car_model = st.text_input("Car Model", placeholder="e.g., Honda Civic 2020")
    odometer = st.number_input("Current Odometer (km)", min_value=0)

with col2:
    last_oil = st.number_input("Last Oil Change (km)", min_value=0)
    city = st.text_input("City for Weather", placeholder="e.g., London")

if st.button("Save & Analyze"):
    # Save to Database
    profile = {"car_model": car_model, "odometer": odometer, "last_oil": last_oil, "city": city}
    db.save_vehicle_profile(profile)
    
    st.divider()
    
    # --- STEP 2: BRAIN CALCULATIONS ---
    st.header("2. Safety Analysis")
    
    # Get Weather Risk
    w_score, w_desc = logic.get_weather_risk(city)
    
    # Get AI Oil Interval
    recommended_interval = logic.get_oil_interval(car_model)
    km_since_oil = odometer - last_oil
    
    # Simple Math for Maintenance Risk
    m_score = (km_since_oil / recommended_interval) * 50
    m_score = min(m_score, 80) # Cap it at 80%
    
    total_risk = w_score + m_score
    
    # --- STEP 3: DISPLAY RESULTS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Weather Risk", f"{w_score}%", w_desc)
    c2.metric("Maintenance Risk", f"{int(m_score)}%", f"{km_since_oil}km since last change")
    c3.metric("Total Road Risk", f"{int(total_risk)}%")

    if total_risk > 50:
        st.error("🚨 HIGH RISK: Drive carefully and check your vehicle maintenance immediately!")
    else:
        st.success("✅ Safe to drive! Roads and vehicle look good.")