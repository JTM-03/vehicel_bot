import streamlit as st
import logic

st.set_page_config(page_title="SL Vehicle Diagnostic AI", layout="wide")
st.title("🛡️ Pro-Diagnostic Vehicle Engine (v2.0)")

with st.form("diagnostic_form"):
    # Basic Specs
    c1, c2, c3 = st.columns(3)
    with c1:
        v_type = st.selectbox("Vehicle Type", ["Petrol/Diesel", "Hybrid", "Full Electric (EV)"])
        model = st.text_input("Model Name", placeholder="e.g. Toyota Vitz / BYD Atto 3")
        m_year = st.number_input("Manufacture Year", 1990, 2026, 2018)
    with c2:
        odo = st.number_input("Odometer Reading (km)", min_value=0)
        district = st.selectbox("Primary District", ["Colombo", "Kandy", "Galle", "Nuwara Eliya", "Other"])
    with c3:
        tyre_odo = st.number_input("Odometer at last Tyre Change (km)", 0)
        align = st.selectbox("Alignment Habit", ["Regularly", "Occasionally", "Rarely"])
        pressure = st.selectbox("Pressure Checks", ["Weekly", "Monthly", "Only when low"])

    st.markdown("### 📅 Recent Trip History (Last 3 Records)")
    st.info("Identify threats by selecting all road types encountered in one trip.")
    
    trips = []
    t_cols = st.columns(3)
    road_options = ["Carpeted", "City Traffic", "Potholes/Rough", "Mountain Slopes", "Slippery/Muddy"]
    
    for i in range(3):
        with t_cols[i]:
            st.write(f"**Trip {i+1}**")
            t_date = st.date_input(f"Date", key=f"d{i}", value=None)
            t_km = st.number_input(f"Distance (km)", key=f"k{i}", min_value=0)
            t_roads = st.multiselect(f"Road Types", road_options, key=f"r{i}")
            trips.append({"date": t_date, "km": t_km, "roads": t_roads})

    last_service = st.number_input("Last Major Service (km)", 0)
    submit = st.form_submit_button("Generate Multi-Trip Diagnostic")

if submit:
    # Validate that at least some data exists
    if not model or not trips[0]['date']:
        st.error("Please provide the model name and at least one trip record.")
    else:
        with st.spinner("Analyzing terrain threats and 2026 market costs..."):
            report = logic.get_advanced_report(v_type, model, m_year, odo, district, tyre_odo, align, pressure, last_service, trips)
            st.markdown(report)