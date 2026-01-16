import streamlit as st
import logic

st.set_page_config(page_title="Vehicle Pro Bot", page_icon="🚗")

st.title("🚗 Smart Vehicle Diagnostic")
st.write("Precision advice based on Sri Lankan road conditions.")

with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1:
        car = st.text_input("Car Model", value="Toyota Axio")
        odo = st.number_input("Current Mileage (km)", value=50000)
        last_s = st.number_input("Last Service at (km)", value=45000)
    with c2:
        dist = st.selectbox("District", ["Colombo", "Gampaha", "Kalutara", "Kandy", "Galle"])
        town = st.text_input("Town", value="Kesbewa")
        repairs = st.text_area("Recent Repairs", placeholder="e.g., Replaced battery")

    submit = st.form_submit_button("Generate Professional Report")

if submit:
    with st.spinner("Analyzing environment and vehicle data..."):
        report = logic.get_detailed_report(car, odo, last_s, repairs, dist, town)
        st.markdown("---")
        st.subheader("📋 Mechanic's Report")
        st.info(report)