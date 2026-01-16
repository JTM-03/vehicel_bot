import streamlit as st
import database as db
import logic

st.set_page_config(page_title="Vehicle Safety Bot", layout="wide")
st.title("🚗 AI Vehicle Safety Assistant")

# --- 1. DATA INPUT ---
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Database (Reset)"):
        # Optional: You can add a reset function later
        st.write("Reset requested")

col1, col2 = st.columns(2)
with col1:
    car_model = st.text_input("Car Model", placeholder="e.g., Toyota Prius 2015")
    odometer = st.number_input("Current Odometer (km)", min_value=0)
with col2:
    last_oil = st.number_input("Last Oil Change (km)", min_value=0)
    city = st.text_input("Current City", placeholder="e.g., New York")

if st.button("Analyze Safety & Fixes"):
    with st.spinner('AI is analyzing your vehicle safety...'):
        # Database Save
        profile = {"car_model": car_model, "odometer": odometer, "last_oil": last_oil, "city": city}
        db.save_vehicle_profile(profile)
        
        # Logic Calculations
        recommended_interval = logic.get_oil_interval(car_model)
        km_since_oil = odometer - last_oil
        w_score, w_desc = logic.get_weather_risk(city)
        
        # Risk Score Calculation
        m_score = min((km_since_oil / recommended_interval) * 60, 80)
        total_risk = w_score + m_score

        # --- DISPLAY RESULTS ---
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Road Weather", f"{w_score}% Risk", w_desc)
        c2.metric("Vehicle Health", f"{int(m_score)}% Risk", f"{km_since_oil}km since service")
        c3.metric("Total Safety Score", f"{int(100 - total_risk)}%", delta_color="inverse")

        # --- AI FIX-IT LIST ---
        st.subheader("🛠️ Recommended Maintenance Fixes")
        advice = logic.get_maintenance_advice(car_model, km_since_oil, w_desc)
        st.info(advice)

        if total_risk > 60:
            st.error("🚨 WARNING: High risk detected! Visit a mechanic soon.")
        elif total_risk > 30:
            st.warning("⚠️ ATTENTION: Some maintenance is required to stay safe.")
        else:
            st.success("✅ Your vehicle is in great shape for current conditions.")