import streamlit as st
import database as db
import logic

st.set_page_config(page_title="Pro Vehicle Bot", layout="wide", page_icon="🔧")

st.title("🔧 Smart Mechanic AI")
st.caption("Context-Aware Vehicle Diagnostics for Sri Lankan Roads")

# --- INPUT SECTION ---
with st.form("analysis_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚙 Vehicle")
        car_model = st.text_input("Car Model", placeholder="e.g. Toyota Axio 2018")
        odometer = st.number_input("Odometer (km)", min_value=0, step=100)
        last_oil = st.number_input("Last Service (km)", min_value=0, step=100)

    with col2:
        st.subheader("📍 Location Context")
        
        # LOGIC IMPROVEMENT: Dropdown for consistent logic mapping
        district = st.selectbox(
            "Select Your Main Driving District",
            ["Colombo", "Gampaha", "Kalutara", "Kandy", "Nuwara Eliya", 
             "Galle", "Matara", "Hambantota", "Jaffna", "Trincomalee", 
             "Batticaloa", "Anuradhapura", "Polonnaruwa", "Kurunegala", 
             "Puttalam", "Ratnapura", "Badulla", "Monaragala", "Kegalle", 
             "Matale", "Mannar", "Mullaitivu", "Vavuniya", "Kilinochchi", "Ampara"]
        )
        
        town = st.text_input("Nearest Town (for Weather)", placeholder="e.g. Piliyandala")
        recent_repairs = st.text_area("Recent Repairs", placeholder="e.g. New battery...")

    submitted = st.form_submit_button("🔍 Run Full Diagnostic")

if submitted:
    if not car_model or not town:
        st.error("Please fill in Car Model and Town.")
    else:
        with st.spinner(f'Analyzing terrain risks for {district} & fetching weather...'):
            
            # 1. Fetch Data
            # Note: We pass the Town for weather, but District for Logic
            w_risk, w_desc = logic.get_weather_risk(town)
            ai_report = logic.get_detailed_report(car_model, odometer, last_oil, recent_repairs, w_desc, district)
            
            # 2. Logic for Display
            env_context = logic.get_environment_context(district)
            
            # --- DASHBOARD ---
            st.divider()
            
            # Dynamic Context Banner
            if "MOUNTAIN" in env_context:
                st.warning(f"⛰️ **TERRAIN ALERT:** You are driving in Hilly areas. {env_context}")
            elif "COASTAL" in env_context:
                st.info(f"🌊 **COASTAL ALERT:** Saltwater risk detected. {env_context}")
            elif "TRAFFIC" in env_context:
                st.warning(f"🚦 **CITY ALERT:** Heavy traffic area. {env_context}")
            
            # Report
            st.markdown("### 📋 The Mechanic's Verdict")
            st.write(ai_report)
            
            # Weather Widget
            st.caption(f"Current Local Weather in {town}: {w_desc}")