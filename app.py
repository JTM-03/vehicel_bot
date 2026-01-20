import streamlit as st
import logic
from datetime import datetime

st.set_page_config(page_title="SL AI Mechanic 2026", layout="wide")

# 1. Session State for Persistent History
if "history_log" not in st.session_state: st.session_state.history_log = []
if "vehicle_data" not in st.session_state: 
    st.session_state.vehicle_data = {"model": "", "city": "", "odo": 0}

districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]

st.title("🚜 Sri Lanka Pro-Vehicle Engine (2026)")

tab1, tab2, tab3 = st.tabs(["📋 Manual Diagnostic", "🤳 Photo Chat", "📜 History"])

# --- TAB 1: FORM WITH TRIP HISTORY RESTORED ---
with tab1:
    with st.form("main_form"):
        st.subheader("📍 Location & Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            v_type = st.selectbox("Vehicle", ["Petrol/Diesel Car", "Hybrid", "EV", "Motorbike", "Three-Wheeler"])
            model = st.text_input("Model", placeholder="e.g. Pulsar 150 / Wagon R")
        with c2:
            district = st.selectbox("District", sorted(districts))
            city = st.text_input("Nearest City", placeholder="e.g. Maharagama")
        with c3:
            odo = st.number_input("Odometer (km)", min_value=0, step=500)
            m_year = st.number_input("Year", 1990, 2026, 2018)

        st.divider()
        st.subheader("🔧 Maintenance & 🛣️ Last 3 Trips")
        m1, m2 = st.columns(2)
        with m1:
            s_odo = st.number_input("Last Service (km)", min_value=0, step=500)
            a_odo = st.number_input("Last Alignment (km)", min_value=0, step=500)
        
        with m2:
            trips = []
            for i in range(3):
                t_km = st.number_input(f"Trip {i+1} Distance (km)", min_value=0, step=10, key=f"t{i}")
                t_road = st.multiselect(f"Road Type {i+1}", ["Carpeted", "City", "Mountain", "Rough"], key=f"r{i}")
                trips.append({"km": t_km, "road": t_road})

        submit = st.form_submit_button("Generate Predictive Report")

    if submit:
        report = logic.get_advanced_report(v_type, model, m_year, odo, district, city, 0, a_odo, s_odo, trips)
        st.session_state.history_log.append({"date": datetime.now().strftime("%Y-%m-%d"), "model": model, "type": "Diagnostic", "content": report})
        st.markdown(report)

# --- TAB 2: PHOTO CHAT ---
with tab2:
    st.subheader("🤳 AI Photo Mechanic")
    st.info("Upload a photo and ask the bot about errors or maintenance.")
    photo = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if photo:
        st.image(photo, width=300)
        query = st.chat_input("Ask a question about this photo...")
        if query:
            context = f"{model} in {city}, {district}"
            ans = logic.analyze_vision_chat(photo, query, context)
            st.chat_message("assistant").write(ans)
            st.session_state.history_log.append({"date": "Photo Analysis", "model": model, "type": "Chat", "content": ans})

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("📜 Your Records")
    if not st.session_state.history_log:
        st.write("No history available yet.")
    else:
        for entry in reversed(st.session_state.history_log):
            with st.expander(f"🕒 {entry['date']} - {entry['model']} ({entry['type']})"):
                st.markdown(entry['content'])