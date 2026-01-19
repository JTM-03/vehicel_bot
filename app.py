import streamlit as st
import logic

st.set_page_config(page_title="SL Vehicle AI", layout="wide")
st.title("🚜 Sri Lanka Pro-Diagnostic Engine (2026 Edition)")

districts = [
    "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", 
    "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", 
    "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", 
    "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"
]

with st.form("main_form"):
    st.subheader("📍 Location & Environment")
    l1, l2 = st.columns(2)
    with l1:
        district = st.selectbox("Select District", sorted(districts))
    with l2:
        city = st.text_input("Nearest City", placeholder="e.g. Maharagama, Peradeniya, Weligama")

    st.divider()
    st.subheader("🚗 Vehicle Profile")
    c1, c2, c3 = st.columns(3)
    with c1:
        v_type = st.selectbox("Type", ["Petrol/Diesel Car", "Hybrid Car", "Full Electric (EV)", "Motor Bicycle", "Three-Wheeler"])
        model = st.text_input("Model", placeholder="e.g. Pulsar 150 / Bajaj RE / Axio")
    with c2:
        # min_value=0 prevents minus values
        odo = st.number_input("Odometer (km)", min_value=0, step=500)
        m_year = st.number_input("Year", 1990, 2026, 2018)
    with c3:
        tyre_odo = st.number_input("Last Tyre Change (Odo km)", min_value=0)
        align_km = st.number_input("Alignment/Service Every (km)", min_value=0, value=5000)

    st.divider()
    st.subheader("📅 Recent Trip History")
    trips = []
    t_cols = st.columns(3)
    for i in range(3):
        with t_cols[i]:
            t_date = st.date_input(f"Trip {i+1} Date", key=f"d{i}", value=None)
            t_km = st.number_input(f"Distance (km)", key=f"k{i}", min_value=0)
            t_roads = st.multiselect(f"Roads", ["Carpeted", "City Traffic", "Potholes/Rough", "Mountain Slopes", "Slippery"], key=f"r{i}")
            trips.append({"date": t_date, "km": t_km, "roads": t_roads})

    submit = st.form_submit_button("Generate Localized Diagnostic")

if submit:
    if not city or not model:
        st.error("Please fill in City and Model details.")
    else:
        with st.spinner(f"Analyzing threats for {city}..."):
            report = logic.get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_km, "Standard", 0, trips)
            st.markdown(report)
            if st.button("🔄 Start New Diagnostic"):
                st.rerun()