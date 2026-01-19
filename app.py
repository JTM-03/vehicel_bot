import streamlit as st
import logic

st.set_page_config(page_title="SL AI Diagnostic", layout="wide")

# 1. Initialize Session State for Chat Updates
if "vehicle_data" not in st.session_state:
    st.session_state.vehicle_data = {
        "v_type": "Petrol/Diesel Car", "model": "", "m_year": 2018,
        "odo": 0, "district": "Colombo", "city": "", "tyre_odo": 0,
        "align_odo": 0, "service_odo": 0, "pressure": "Regular"
    }

st.title("🛡️ Sri Lanka Pro-Vehicle AI Engine (2026)")

tab1, tab2 = st.tabs(["📋 Manual Diagnostic Form", "💬 AI Chat Update"])

with tab1:
    with st.form("diagnostic_form"):
        st.subheader("📍 Location & Vehicle Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            v_type = st.selectbox("Vehicle Type", ["Petrol/Diesel Car", "Hybrid Car", "Full Electric (EV)", "Motor Bicycle", "Three-Wheeler"], index=0)
            # Distinct placeholder to avoid confusion
            model = st.text_input("Vehicle Model", value=st.session_state.vehicle_data["model"], placeholder="e.g. Bajaj RE / Honda Vezel / Pulsar")
            m_year = st.number_input("Manufacture Year", 1990, 2026, 2018)
        with c2:
            district = st.selectbox("District", sorted(["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]))
            city = st.text_input("Nearest City", value=st.session_state.vehicle_data["city"], placeholder="e.g. Maharagama, Peradeniya, Matara City")
        with c3:
            # step=500 adds the +/- buttons as requested. min_value=0 prevents negative.
            odo = st.number_input("Current Odometer (km)", min_value=0, step=500, value=st.session_state.vehicle_data["odo"])
            pressure = st.selectbox("Tyre Pressure Habits", ["Regular", "Only when low"])

        st.divider()
        st.subheader("🔧 Maintenance Records (Manual Entry)")
        m1, m2, m3 = st.columns(3)
        with m1:
            tyre_odo = st.number_input("Odo at last Tyre Change (km)", min_value=0, step=500)
        with m2:
            align_odo = st.number_input("Odo at last Wheel Alignment (km)", min_value=0, step=500)
        with m3:
            service_odo = st.number_input("Odo at last Full Service (km)", min_value=0, step=500)

        st.markdown("### 📅 Recent 3 Trips")
        trips = []
        t_cols = st.columns(3)
        for i in range(3):
            with t_cols[i]:
                t_km = st.number_input(f"Trip {i+1} km", min_value=0, step=10, key=f"k{i}")
                t_roads = st.multiselect(f"Roads {i+1}", ["Carpeted", "City", "Rough", "Mountain"], key=f"r{i}")
                trips.append({"date": None, "km": t_km, "roads": t_roads})

        submit = st.form_submit_button("Generate Predictive Report")

    if submit:
        if not model or not city:
            st.error("Please provide both Model Name and City.")
        else:
            report = logic.get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, pressure, service_odo, trips)
            st.markdown(report)

with tab2:
    st.info("You can talk to the bot to update your details. (e.g., 'I changed my tyres at 45000km')")
    chat_input = st.chat_input("Update your vehicle details here...")
    if chat_input:
        with st.chat_message("user"): st.write(chat_input)
        response = logic.process_chat_update(chat_input, st.session_state.vehicle_data)
        with st.chat_message("assistant"):
            st.write(f"Updated! I've logged your new data. Please refresh the 'Manual Form' to see changes.")
            st.code(response) # In a production app, we would parse this JSON into session_state.