import streamlit as st
import logic

st.set_page_config(page_title="Pro-Vehicle Diagnostic", layout="wide")
st.title("🛡️ Advanced Vehicle Safety & Diagnostic Engine")

# Form wrapper
with st.form("master_diagnostic_form"):
    # Section 1: Vehicle Profile
    st.subheader("🚙 Vehicle Profile")
    c1, c2, c3 = st.columns(3)
    with c1:
        v_type = st.selectbox("Vehicle Type", ["Petrol/Diesel", "Hybrid", "Full Electric (EV)"])
        model = st.text_input("Model Name", placeholder="e.g. Nissan Leaf / Honda Vezel")
        m_year = st.number_input("Manufacture Year", 1980, 2026, 2018)
    with c2:
        odo = st.number_input("Total Odometer (km)", min_value=0)
        district = st.selectbox("Primary District", ["Colombo", "Kandy", "Galle", "Nuwara Eliya", "Other"])
    with c3:
        tyre_odo = st.number_input("Odometer at last Tyre Change (km)", min_value=0)
        # KM-based alignment as requested
        align_km = st.number_input("Wheel Alignment Frequency (Every X km)", value=5000, step=500)
        pressure = st.selectbox("Tyre Pressure Checks", ["Weekly", "Monthly", "Only when low"])

    # Section 2: Three Trip Records
    st.markdown("---")
    st.subheader("📅 Recent Trip History (Last 3 Rides)")
    st.caption("Select multiple road types if the trip covered different terrains.")
    
    road_options = ["Carpeted", "City Traffic", "Potholes/Rough", "Mountain Slopes", "Slippery/Muddy"]
    trips = []
    t_cols = st.columns(3)
    
    for i in range(3):
        with t_cols[i]:
            st.write(f"**Trip Record {i+1}**")
            t_date = st.date_input(f"Date", key=f"date_{i}", value=None)
            t_km = st.number_input(f"Distance (km)", key=f"km_{i}", min_value=0)
            t_roads = st.multiselect(f"Road Conditions", road_options, key=f"road_{i}")
            trips.append({"date": t_date, "km": t_km, "roads": t_roads})

    last_service = st.number_input("Last Major Service/Oil Change (km)", min_value=0)
    
    submit = st.form_submit_button("Generate Predictive Report")

# Output Section
if submit:
    if not model or not trips[0]['date']:
        st.error("Missing Data: Please enter the Vehicle Model and at least one Trip Date.")
    else:
        with st.spinner("Analyzing mechanical data and terrain severity..."):
            report = logic.get_advanced_report(v_type, model, m_year, odo, district, tyre_odo, align_km, pressure, last_service, trips)
            st.divider()
            st.markdown(report)
            
            # Refresh functionality
            if st.button("🔄 Clear and Start New Diagnostic"):
                st.rerun()