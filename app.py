import streamlit as st
import database as db
import logic

st.set_page_config(page_title="Pro Vehicle Bot", layout="wide", page_icon="🔧")

st.title("🔧 Pro Vehicle Health Monitor")
st.markdown("Enter your details below for a precision maintenance report.")

# --- SIDEBAR: HISTORY ---
with st.sidebar:
    st.header("📂 User History")
    if st.button("Load Last Saved Profile"):
        profile = db.get_vehicle_profile()
        if profile:
            st.success("Loaded!")
            st.json(profile)
        else:
            st.warning("No history found.")

# --- MAIN INPUT FORM ---
with st.form("analysis_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚙 Vehicle Details")
        car_model = st.text_input("Car Model", placeholder="e.g. Toyota Axio 2018 WXB")
        odometer = st.number_input("Current Odometer (km)", min_value=0, step=100)
        last_oil = st.number_input("Last Service Mileage (km)", min_value=0, step=100)

    with col2:
        st.subheader("📍 Location & History")
        # specific prompt for accuracy
        location = st.text_input("Specific Location", placeholder="e.g. Piliyandala, Colombo") 
        recent_repairs = st.text_area("Recent Repairs (Optional)", placeholder="e.g. Changed battery last month, new tires...")

    submitted = st.form_submit_button("📊 Generate Professional Report")

# --- ANALYSIS LOGIC ---
if submitted:
    if not car_model or not location:
        st.error("Please enter Car Model and Location to proceed.")
    else:
        with st.spinner('🔍 Analyzing engine data, weather patterns, and maintenance logs...'):
            
            # 1. Save Data
            db.save_vehicle_profile({
                "car": car_model, 
                "odo": odometer, 
                "last_service": last_oil, 
                "repairs": recent_repairs
            })

            # 2. Get Data
            interval = logic.get_oil_interval(car_model)
            w_risk, w_desc = logic.get_weather_risk(location)
            
            # 3. Calculate Basic Health
            km_driven = odometer - last_oil
            health_score = 100 - min(((km_driven / interval) * 100), 100)
            
            # 4. Get AI Report
            ai_report = logic.get_detailed_report(car_model, odometer, last_oil, recent_repairs, w_desc)

            # --- DASHBOARD DISPLAY ---
            st.divider()
            
            # Top Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Weather Condition", w_desc, f"-{w_risk}% Safety")
            m2.metric("Next Oil Change Due", f"{last_oil + interval} km", f"{interval - km_driven} km remaining")
            
            if health_score > 70:
                m3.metric("Vehicle Health Score", f"{int(health_score)}%", "Excellent")
            elif health_score > 30:
                m3.metric("Vehicle Health Score", f"{int(health_score)}%", "Fair", delta_color="off")
            else:
                m3.metric("Vehicle Health Score", f"{int(health_score)}%", "Critical", delta_color="inverse")

            # The Detailed Report
            st.subheader("📋 Professional Mechanic's Report")
            st.info(ai_report)