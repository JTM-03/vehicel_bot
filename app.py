import streamlit as st
import logic

st.set_page_config(page_title="Pro Vehicle Bot", layout="wide")

st.title("🛡️ Advanced Vehicle Safety & Trip Tracker")

# Using columns for better layout
with st.form("diagnostics_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Location & Vehicle")
        vehicle = st.text_input("Vehicle Model", value="Toyota Axio")
        district = st.selectbox("District", ["Colombo", "Kandy", "Nuwara Eliya", "Galle", "Kesbewa"])
        town = st.text_input("Town", value="Kesbewa")
        odo = st.number_input("Odometer (km)", value=60000)
        fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Hybrid"])

    with col2:
        st.subheader("⚙️ Maintenance Status")
        last_service = st.number_input("Last Oil Change (km)", value=55000)
        brake_age = st.number_input("Last Brake Pad Change (km ago)", value=10000)
        tyre_cond = st.select_slider("Tyre Condition", options=["Low", "Fair", "Good", "New"], value="Good")
        road_type = st.selectbox("Primary Road Type", ["Highway", "City/Urban", "Rough/Gravel", "Steep/Hills"])

    st.markdown("---")
    st.subheader("📅 Recent Trip Log (Last 3 Rides)")
    t1, t2, t3 = st.columns(3)
    trip1 = t1.number_input("Trip 1 Distance (km)", value=5)
    trip2 = t2.number_input("Trip 2 Distance (km)", value=8)
    trip3 = t3.number_input("Trip 3 Distance (km)", value=4)

    submit = st.form_submit_button("Generate Predictive Analysis")

if submit:
    # Package trips into a list
    trips = [trip1, trip2, trip3]
    
    with st.spinner("Calculating safety risks..."):
        report = logic.generate_predictive_report(
            vehicle, odo, last_service, brake_age, 
            tyre_cond, road_type, district, town, trips
        )
        st.markdown(report)