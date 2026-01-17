import streamlit as st
import logic

st.set_page_config(page_title="Sri Lanka Vehicle AI", layout="wide")
st.title("🛡️ Pro-Diagnostic Vehicle Engine")

with st.form("entry_form"):
    st.subheader("🚗 Vehicle & Usage Specs")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        v_type = st.selectbox("Fuel Type", ["Petrol/Diesel", "Hybrid", "Full Electric (EV)"])
        model = st.text_input("Model Name", placeholder="Type model here...")
        m_year = st.number_input("Manufacture Year", min_value=1980, max_value=2026, value=2015)
    
    with col2:
        odo = st.number_input("Current Odometer (km)", min_value=0, step=1000)
        road_env = st.selectbox("Road Condition", ["Carpeted", "City Traffic", "Potholes/Rough", "Mountain Slopes"])
        district = st.selectbox("District", ["Colombo", "Kandy", "Galle", "Other"])

    with col3:
        tyre_odo = st.number_input("Odometer at last Tyre Change (km)", min_value=0)
        align = st.selectbox("Wheel Alignment Frequency", ["Every 5k km", "Every 10k km", "Rarely"])
        pressure = st.selectbox("Tyre Pressure Checks", ["Weekly", "Monthly", "Only when low"])

    st.markdown("---")
    st.subheader("📅 Recent Trip History (To check for Oil/Battery Stagnation)")
    r1, r2 = st.columns(2)
    with r1:
        d1 = st.date_input("Last Ride Date", value=None)
        k1 = st.number_input("Last Ride distance (km)", min_value=0)
    with r2:
        d2 = st.date_input("Previous Ride Date", value=None)
        k2 = st.number_input("Previous Ride distance (km)", min_value=0)

    last_service = st.number_input("Last Major Service (km)", min_value=0)
    
    submit = st.form_submit_button("Generate Diagnostic Report")

if submit:
    usage = {"dates": [d1, d2], "km": [k1, k2]}
    report = logic.get_advanced_report(v_type, model, m_year, odo, district, road_env, tyre_odo, align, pressure, last_service, usage)
    st.markdown(report)