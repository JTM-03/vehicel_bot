import streamlit as st
import database as db

st.set_page_config(page_title="Vehicle Safety Bot", page_icon="🚗")

st.title("🚗 Vehicle Safety Bot")

# --- PHASE 2: FINAL EXAM (Save/Load Data) ---
st.header("1. Your Vehicle Profile")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    car_model = st.text_input("Car Model", placeholder="e.g. Toyota Corolla 2018")
    odometer = st.number_input("Current Odometer (km)", min_value=0, step=100)

with col2:
    last_oil_change = st.number_input("Last Oil Change at (km)", min_value=0, step=100)
    city = st.text_input("Your City", placeholder="e.g. Colombo")

if st.button("Save Profile to Database"):
    profile_data = {
        "car_model": car_model,
        "odometer": odometer,
        "last_oil_change": last_oil_change,
        "city": city
    }
    
    success = db.save_vehicle_profile(profile_data)
    if success:
        st.success(f"✅ Saved {car_model} to MongoDB!")
    else:
        st.error("❌ Failed to save. Check logs.")

# --- CHECK SAVED DATA ---
if st.checkbox("Show my saved data from MongoDB"):
    saved_profile = db.get_vehicle_profile()
    if saved_profile:
        st.write(saved_profile)
    else:
        st.warning("No profile found in database.")

st.divider()