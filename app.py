# Add these new inputs to your form
with st.expander("🛠️ Advanced Wear & Tear Details"):
    c1, c2 = st.columns(2)
    with c1:
        tyre_cond = st.selectbox("Tyre Condition", ["New", "Good (Tread visible)", "Fair (Wearing out)", "Low (Bald/Slippery)"])
        brake_age = st.number_input("How many km since last Brake Pad change?", value=5000)
    with c2:
        road_type = st.selectbox("Primary Road Type", ["Well Paved (Highway)", "Urban (City Roads)", "Rough (Potholes/Gravel)", "Steep/Hilly"])
        avg_speed = st.slider("Average Driving Speed (km/h)", 20, 100, 40)

fuel_type = st.radio("Fuel Type", ["Petrol", "Diesel", "Hybrid", "Electric"], horizontal=True)