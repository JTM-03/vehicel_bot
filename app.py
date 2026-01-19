import streamlit as st
import logic
from datetime import datetime

st.set_page_config(page_title="SL AI Mechanic 2026", layout="wide")

# 1. Session State Initialization
if "history" not in st.session_state: st.session_state.history = []
if "vehicle_data" not in st.session_state:
    st.session_state.vehicle_data = {"odo": 0, "model": "", "district": "Colombo", "city": ""}

districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]

st.title("🚜 Sri Lanka Pro-Diagnostic Engine (2026)")

tab1, tab2, tab3 = st.tabs(["📋 Manual Diagnostic", "💬 Chat & Photo Analysis", "📜 History"])

# --- TAB 1: MANUAL FORM ---
with tab1:
    with st.form("manual_form"):
        st.subheader("📍 Location & Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            v_type = st.selectbox("Vehicle Type", ["Petrol/Diesel Car", "Hybrid Car", "Full Electric (EV)", "Motor Bicycle", "Three-Wheeler"])
            model = st.text_input("Vehicle Model", placeholder="e.g. Suzuki Wagon R / Pulsar 150")
            m_year = st.number_input("Year", 1990, 2026, 2018)
        with c2:
            district = st.selectbox("District", sorted(districts))
            city = st.text_input("Nearest City", placeholder="e.g. Gampaha, Kaduwela")
        with c3:
            # Step=500 and min_value=0 as requested
            odo = st.number_input("Odometer (km)", min_value=0, step=500)
            pressure = st.selectbox("Tyre Pressure Habits", ["Regular", "Irregular"])

        st.subheader("🔧 Maintenance Records")
        m1, m2, m3 = st.columns(3)
        with m1: tyre_odo = st.number_input("Last Tyre Change (km)", min_value=0, step=500)
        with m2: align_odo = st.number_input("Last Alignment (km)", min_value=0, step=500)
        with m3: service_odo = st.number_input("Last Service (km)", min_value=0, step=500)

        submit = st.form_submit_button("Generate Predictive Report")

    if submit:
        report = logic.get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, pressure, service_odo, [])
        st.session_state.history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "model": model, "report": report})
        st.markdown(report)

# --- TAB 2: VISION CHAT ---
with tab2:
    st.subheader("🤳 AI Photo Mechanic")
    st.info("Upload a photo of a part (tyre, engine, chain) and ask the bot anything.")
    
    chat_image = st.file_uploader("Upload Vehicle Photo", type=["jpg", "png", "jpeg"])
    if chat_image:
        st.image(chat_image, width=300)
        user_query = st.chat_input("Ask about this photo (e.g., 'Is this rust normal for Colombo?')")
        
        if user_query:
            context = f"{model} ({v_type}) in {city}, {district}"
            with st.spinner("Analyzing..."):
                response = logic.analyze_photo_and_chat(chat_image, user_query, context)
                st.chat_message("assistant").write(response)
                # Save to history
                st.session_state.history.append({"date": "Photo Chat", "model": model, "report": response})

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("📜 Diagnostic Records")
    if not st.session_state.history:
        st.write("No history found. Start a diagnostic to see records here.")
    else:
        for entry in reversed(st.session_state.history):
            with st.expander(f"🕒 {entry['date']} - {entry['model']}"):
                st.markdown(entry['report'])