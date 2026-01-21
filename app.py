import streamlit as st
import logic
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="SL AI Mechanic 2026", layout="wide")

# 1. Session State for Persistent History
if "history_log" not in st.session_state: 
    st.session_state.history_log = []
if "vehicle_data" not in st.session_state: 
    st.session_state.vehicle_data = {"model": "", "city": "", "odo": 0}
if "trips_data" not in st.session_state:
    st.session_state.trips_data = []

districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]

st.title("🚜 Sri Lanka Pro-Vehicle Engine (2026)")
st.markdown("---")

# Display current trips status
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Active Trips", len(st.session_state.trips_data), "trips tracked")
with col2:
    total_km = sum([t.get("km", 0) for t in st.session_state.trips_data])
    st.metric("Total Trip Distance", f"{total_km} km", "collected")
with col3:
    if st.session_state.trips_data:
        latest_date = max([t.get("date", "") for t in st.session_state.trips_data])
        st.metric("Latest Trip", latest_date, "recorded")
    else:
        st.metric("Latest Trip", "None", "recorded")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Manual Diagnostic", "🤳 Photo Chat", "📊 Trip Data", "📜 History"])

# --- TAB 1: FORM WITH TRIP DATA COLLECTION ---
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
        st.subheader("🔧 Maintenance History")
        m1, m2 = st.columns(2)
        with m1:
            s_odo = st.number_input("Last Service (km)", min_value=0, step=500)
        with m2:
            a_odo = st.number_input("Last Alignment (km)", min_value=0, step=500)
        
        st.divider()
        st.subheader("🛣️ Recent Trip Data (Last 3 Trips)")
        st.info("💡 Tip: Enter your recent trips to get accurate maintenance predictions based on actual road conditions.")
        
        trips = []
        if st.session_state.trips_data:
            st.write("**Your stored trips:**")
            for idx, trip in enumerate(st.session_state.trips_data[-3:]):
                st.caption(f"📅 {trip.get('date', 'N/A')} | 🛣️ {trip.get('km', 0)} km | 🗺️ {', '.join(trip.get('road', []))}")
            
            if len(st.session_state.trips_data) >= 3:
                st.success("✓ All 3 trips recorded! Ready for analysis.")
                trips = [{"km": t.get("km", 0), "road": t.get("road", []), "date": t.get("date", "")} for t in st.session_state.trips_data[-3:]]
        
        st.write("**Enter Trip Details:**")
        t1, t2, t3 = st.columns(3)
        
        with t1:
            st.write("**Trip 1**")
            t1_km = st.number_input("Distance (km)", min_value=0, step=10, key="t1_km", value=0)
            t1_road = st.multiselect("Road Type", ["Carpeted", "City", "Mountain", "Rough"], key="t1_road", default=[])
            t1_date = st.date_input("Date", key="t1_date", value=datetime.now().date())
        
        with t2:
            st.write("**Trip 2**")
            t2_km = st.number_input("Distance (km)", min_value=0, step=10, key="t2_km", value=0)
            t2_road = st.multiselect("Road Type", ["Carpeted", "City", "Mountain", "Rough"], key="t2_road", default=[])
            t2_date = st.date_input("Date", key="t2_date", value=(datetime.now() - timedelta(days=1)).date())
        
        with t3:
            st.write("**Trip 3**")
            t3_km = st.number_input("Distance (km)", min_value=0, step=10, key="t3_km", value=0)
            t3_road = st.multiselect("Road Type", ["Carpeted", "City", "Mountain", "Rough"], key="t3_road", default=[])
            t3_date = st.date_input("Date", key="t3_date", value=(datetime.now() - timedelta(days=2)).date())
        
        # Only add new trips if they have data
        if not trips:  # If no stored trips, use the new entries
            trips = [
                {"km": t1_km, "road": t1_road, "date": str(t1_date)},
                {"km": t2_km, "road": t2_road, "date": str(t2_date)},
                {"km": t3_km, "road": t3_road, "date": str(t3_date)}
            ]

        submit = st.form_submit_button("🔍 Generate Predictive Report")

    if submit:
        if not model:
            st.error("❌ Please enter vehicle model")
        elif not any([t["km"] > 0 for t in trips]):
            st.error("❌ Please enter at least one trip distance")
        else:
            # Store trip data
            for trip in trips:
                if trip["km"] > 0:  # Only store non-zero trips
                    st.session_state.trips_data.append(trip)
            
            report = logic.get_advanced_report(v_type, model, m_year, odo, district, city, 0, a_odo, s_odo, trips)
            st.session_state.history_log.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                "model": model, 
                "type": "Diagnostic", 
                "content": report
            })
            
            st.success("✅ Diagnostic Report Generated!")
            st.markdown(report)
            st.balloons()

# --- TAB 2: PHOTO CHAT ---
with tab2:
    st.subheader("🤳 AI Photo Mechanic")
    st.info("📸 Upload a photo and ask the bot about errors or maintenance.")
    photo = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if photo:
        st.image(photo, width=300)
        query = st.chat_input("Ask a question about this photo...")
        if query:
            context = f"{st.session_state.vehicle_data.get('model', 'Vehicle')} in {st.session_state.vehicle_data.get('city', 'Location')}"
            ans = logic.analyze_vision_chat(photo, query, context)
            st.chat_message("assistant").write(ans)
            st.session_state.history_log.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                "model": st.session_state.vehicle_data.get('model', 'Vehicle'), 
                "type": "Photo Analysis", 
                "content": ans
            })

# --- TAB 3: TRIP DATA VISUALIZATION ---
with tab3:
    st.subheader("📊 Your Trip Data Collection")
    
    if not st.session_state.trips_data:
        st.info("📌 No trips recorded yet. Add trips in the Manual Diagnostic tab to see data here.")
    else:
        # Display all recorded trips
        st.write(f"**Total Trips Recorded:** {len(st.session_state.trips_data)}")
        
        # Create a DataFrame for better visualization
        trip_df = pd.DataFrame(st.session_state.trips_data)
        trip_df_display = trip_df.copy()
        trip_df_display['road'] = trip_df_display['road'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        st.dataframe(trip_df_display, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Distance", f"{trip_df['km'].sum()} km")
        with col2:
            st.metric("Average Distance", f"{trip_df['km'].mean():.1f} km")
        with col3:
            st.metric("Trips Count", len(st.session_state.trips_data))
        
        # Road type distribution
        st.write("**Road Type Distribution:**")
        all_roads = []
        for roads in trip_df['road']:
            all_roads.extend(roads if isinstance(roads, list) else [])
        
        if all_roads:
            road_counts = pd.Series(all_roads).value_counts()
            st.bar_chart(road_counts)
        
        st.divider()
        
        # Clear trips button
        if st.button("🗑️ Clear All Trip Data", help="This will reset all recorded trips"):
            st.session_state.trips_data = []
            st.success("✓ Trip data cleared!")
            st.rerun()

# --- TAB 4: HISTORY ---
with tab4:
    st.subheader("📜 Your Diagnostic Records")
    if not st.session_state.history_log:
        st.info("📌 No diagnostic reports yet. Generate a report in the Manual Diagnostic tab.")
    else:
        st.write(f"**Total Records:** {len(st.session_state.history_log)}")
        st.divider()
        
        for idx, entry in enumerate(reversed(st.session_state.history_log)):
            with st.expander(f"🕒 {entry['date']} - {entry['model']} ({entry['type']})"):
                st.markdown(entry['content'])
        
        st.divider()
        
        # Clear history button
        if st.button("🗑️ Clear All History", help="This will delete all diagnostic reports"):
            st.session_state.history_log = []
            st.success("✓ History cleared!")
            st.rerun()
