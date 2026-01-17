import streamlit as st
import logic
from datetime import date

st.set_page_config(page_title="Pro Vehicle AI", layout="wide")
st.title("🛡️ Smart Vehicle Diagnostic Engine")

with st.form("master_form"):
    # --- Section 1: Vehicle Specs ---
    st.subheader("🚗 Vehicle Profile")
    c1, c2, c3 = st.columns(3)
    with c1:
        v_type = st.radio("Vehicle Type", ["Petrol/Diesel", "Hybrid", "Full Electric (EV)"])
        model = st.text_input("Model Name", placeholder="e.g. Nissan Leaf / Toyota Axio")
    with c2:
        m_year = st.number_input("Manufacture Year", min_value=1980, max_value=2026, value=2015)
        odo = st.number_input("Current Odometer (km)", min_value=0, step=1000)
    with c3:
        district = st.selectbox("Driving District", ["Colombo", "Kandy", "Nuwara Eliya", "Galle", "Kesbewa", "Other"])
        road_env = st.selectbox("Primary Roads", ["Carpeted/Highway", "City Traffic", "Potholes/Rough", "Mountain Slopes"])

    # --- Section 2: Tyre Health (The Predictor) ---
    st.markdown("---")
    st.subheader("🛞 Tyre & Alignment History")
    t1, t2, t3 = st.columns(3)
    with t1:
        tyre_change_odo = st.number_input("Odometer at last Tyre Change (km)", min_value=0)
    with t2:
        alignment_freq = st.selectbox("Alignment Frequency", ["Every 5k km", "Every 10k km", "Rarely / Only when pulling"])
    with t3:
        pressure_freq = st.selectbox("Pressure Check Freq", ["Weekly", "Monthly", "Only when low"])

    # --- Section 3: Usage Pattern (Stagnation Check) ---
    st.markdown("---")
    st.subheader("📅 Recent Usage (Last 3 Rides)")
    r1, r2, r3 = st.columns(3)
    trip1_d = r1.date_input("Ride 1 Date", value=None)
    trip1_k = r1.number_input("Ride 1 Distance (km)", min_value=0)
    
    trip2_d = r2.date_input("Ride 2 Date", value=None)
    trip2_k = r2.number_input("Ride 2 Distance (km)", min_value=0)
    
    trip3_d = r3.date_input("Ride 3 Date", value=None)
    trip3_k = r3.number_input("Ride 3 Distance (km)", min_value=0)

    # --- Section 4: Maintenance ---
    st.markdown("---")
    st.subheader("🔧 Maintenance")
    last_service = st.number_input("Last Major Service/Oil Change (km)", min_value=0)
    
    submit = st.form_submit_button("Generate Safety Report")

if submit:
    # Package data
    usage_data = {
        "trips": [trip1_k, trip2_k, trip3_k],
        "dates": [trip1_d, trip2_d, trip3_d]
    }
    
    with st.spinner("Analyzing mechanical threats..."):
        report = logic.get_advanced_report(
            v_type, model, m_year, odo, district, road_env, 
            tyre_change_odo, alignment_freq, pressure_freq, 
            last_service, usage_data
        )
        st.markdown(report)