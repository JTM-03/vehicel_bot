import streamlit as st
import logic
import database
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="SL AI Mechanic 2026", layout="wide")

# 1. Session State for Persistent History
if "history_log" not in st.session_state: 
    st.session_state.history_log = []
if "vehicle_data" not in st.session_state: 
    st.session_state.vehicle_data = {"model": "", "city": "", "odo": 0, "district": "", "v_type": "", "m_year": 2018}
if "trips_data" not in st.session_state:
    st.session_state.trips_data = []
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "user_loaded" not in st.session_state:
    st.session_state.user_loaded = False
if "changes_log" not in st.session_state:
    st.session_state.changes_log = []

districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]

st.title("🚜 Sri Lanka Pro-Vehicle Engine (2026)")
st.markdown("---")

# User Profile Section
st.subheader("👤 User Profile & Identification")
user_col1, user_col2, user_col3, user_col4 = st.columns(4)

with user_col1:
    if st.session_state.current_user_id:
        st.info(f"🔑 User ID: `{st.session_state.current_user_id}`")
    else:
        st.warning("📭 No user loaded")

with user_col2:
    if st.session_state.vehicle_data.get("model"):
        st.success(f"🚗 {st.session_state.vehicle_data.get('v_type', 'Vehicle')}: {st.session_state.vehicle_data.get('model', 'N/A')}")
    else:
        st.info("Enter vehicle model below")

with user_col3:
    if st.session_state.vehicle_data.get("city"):
        st.success(f"📍 {st.session_state.vehicle_data.get('district', 'District')}, {st.session_state.vehicle_data.get('city', 'N/A')}")
    else:
        st.info("Enter location below")

with user_col4:
    if st.session_state.user_loaded:
        st.success("✅ Data Loaded from Database")
    else:
        st.warning("🆕 New User Session")

st.markdown("---")

# User Management Section
st.subheader("🔄 User Management")
manage_col1, manage_col2, manage_col3 = st.columns(3)

with manage_col1:
    # Load existing user
    existing_users = database.get_all_users()
    if existing_users:
        user_options = {f"{u.get('model', 'Unknown')} - {u.get('city', 'Unknown')}": u.get('user_id') for u in existing_users if u.get('user_id')}
        selected_user_label = st.selectbox("📂 Load Existing User", ["🆕 New User"] + list(user_options.keys()))
        
        if selected_user_label != "🆕 New User":
            if st.button("⬇️ Load Selected User"):
                user_id = user_options[selected_user_label]
                user_data = database.get_user_by_id(user_id)
                
                if user_data:
                    st.session_state.current_user_id = user_id
                    st.session_state.vehicle_data = user_data.get("vehicle_data", {})
                    st.session_state.trips_data = user_data.get("trips_data", [])
                    st.session_state.history_log = user_data.get("history_log", [])
                    st.session_state.changes_log = user_data.get("changes_log", [])
                    st.session_state.user_loaded = True
                    st.success(f"✅ Loaded user: {selected_user_label}")
                    st.rerun()

with manage_col2:
    # View all users
    if st.button("📊 View All Users"):
        all_users = database.get_all_users()
        if all_users:
            st.write("**Registered Users:**")
            users_df = pd.DataFrame([{
                "Model": u['model'],
                "City": u['city'],
                "District": u['district'],
                "Created": u.get('created_date', 'N/A')[:10]
            } for u in all_users])
            st.dataframe(users_df, use_container_width=True)
        else:
            st.info("No users in database yet.")

with manage_col3:
    # Clear current session
    if st.button("🗑️ Start New Session"):
        st.session_state.current_user_id = None
        st.session_state.vehicle_data = {"model": "", "city": "", "odo": 0, "district": "", "v_type": "", "m_year": 2018}
        st.session_state.trips_data = []
        st.session_state.user_loaded = False
        st.session_state.history_log = []
        st.session_state.changes_log = []
        st.info("🆕 Session cleared. Ready for new user.")
        st.rerun()

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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Manual Diagnostic", "🤳 Photo Chat", "📊 Trip Data", "📜 History", "📝 Changes Log"])

# --- TAB 1: FORM WITH TRIP DATA COLLECTION ---
with tab1:
    with st.form("main_form"):
        st.subheader("📍 Location & Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            v_types = ["Petrol/Diesel Car", "Hybrid", "EV", "Motorbike", "Three-Wheeler"]
            v_type_default = st.session_state.vehicle_data.get("v_type", "Petrol/Diesel Car")
            v_type_index = v_types.index(v_type_default) if v_type_default in v_types else 0
            v_type = st.selectbox(
                "Vehicle", 
                v_types,
                index=v_type_index
            )
            model = st.text_input(
                "Model", 
                placeholder="e.g. Pulsar 150 / Wagon R",
                value=st.session_state.vehicle_data.get("model", "")
            )
        with c2:
            district = st.selectbox(
                "District", 
                sorted(districts),
                index=sorted(districts).index(st.session_state.vehicle_data.get("district", "Colombo")) if st.session_state.vehicle_data.get("district") in districts else 0
            )
            city = st.text_input(
                "Nearest City", 
                placeholder="e.g. Maharagama",
                value=st.session_state.vehicle_data.get("city", "")
            )
        with c3:
            odo = st.number_input(
                "Odometer (km)", 
                min_value=0, 
                step=500,
                value=int(st.session_state.vehicle_data.get("odo", 0))
            )
            m_year = st.number_input(
                "Year", 
                1990, 
                2026, 
                int(st.session_state.vehicle_data.get("m_year", 2018))
            )

        st.divider()
        st.subheader("🔧 Maintenance History")
        st.info("💾 These values are loaded from database. Edit below if you need to update them.")
        m1, m2 = st.columns(2)
        with m1:
            s_odo = st.number_input(
                "Last Service (km)", 
                min_value=0, 
                step=500,
                value=int(st.session_state.vehicle_data.get("s_odo", 0))
            )
        with m2:
            a_odo = st.number_input(
                "Last Alignment (km)", 
                min_value=0, 
                step=500,
                value=int(st.session_state.vehicle_data.get("a_odo", 0))
            )
        
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

        st.divider()
        col_submit1, col_submit2 = st.columns(2)
        with col_submit1:
            submit = st.form_submit_button("🔍 Generate Predictive Report")
        with col_submit2:
            save_profile = st.form_submit_button("💾 Save User Profile to Database")

    if save_profile:
        if not model or not city or not district:
            st.error("❌ Please enter vehicle model, city, and district to save profile")
        else:
            # Generate user ID
            user_id = database.generate_user_id(model, city)
            
            # Prepare vehicle data
            vehicle_data = {
                "v_type": v_type,
                "model": model,
                "district": district,
                "city": city,
                "odo": odo,
                "m_year": m_year,
                "s_odo": s_odo,
                "a_odo": a_odo
            }
            
            # Save to database
            success = database.save_user_data(
                user_id,
                vehicle_data,
                st.session_state.trips_data,
                st.session_state.history_log
            )
            
            if success:
                st.session_state.current_user_id = user_id
                st.session_state.vehicle_data = vehicle_data
                st.session_state.user_loaded = True
                st.success(f"✅ Profile saved! User ID: `{user_id}`")
                st.info(f"Vehicle: {v_type} - {model} in {city}, {district}")
                st.balloons()
            else:
                st.warning("⚠️ Database connection not available. Data saved in session only.")

    if submit:
        if not model:
            st.error("❌ Please enter vehicle model")
        elif not any([t["km"] > 0 for t in trips]):
            st.error("❌ Please enter at least one trip distance")
        else:
            # Update session state
            st.session_state.vehicle_data = {
                "v_type": v_type,
                "model": model,
                "district": district,
                "city": city,
                "odo": odo,
                "m_year": m_year,
                "s_odo": s_odo,
                "a_odo": a_odo
            }
            
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
            
            # Save to database if user is loaded
            if st.session_state.current_user_id:
                database.save_user_data(
                    st.session_state.current_user_id,
                    st.session_state.vehicle_data,
                    st.session_state.trips_data,
                    st.session_state.history_log
                )
            
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
            if st.session_state.current_user_id:
                database.save_user_data(
                    st.session_state.current_user_id,
                    st.session_state.vehicle_data,
                    st.session_state.trips_data,
                    st.session_state.history_log
                )
            st.success("✓ History cleared!")
            st.rerun()

# --- TAB 5: CHANGES LOG ---
with tab5:
    st.subheader("📝 Changes & Modifications Log")
    
    if st.session_state.current_user_id:
        changes = database.get_changes_log(st.session_state.current_user_id)
        
        if not changes:
            st.info("📌 No changes recorded yet. Start using the app to track changes.")
        else:
            st.write(f"**Total Changes:** {len(changes)}")
            st.divider()
            
            # Display changes in reverse order (newest first)
            for change in reversed(changes):
                change_type = change.get("field", "unknown")
                timestamp = change.get("timestamp", "N/A")
                
                if change_type == "last_service_odometer":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"🕐 {timestamp[:16]}")
                    with col2:
                        st.caption(f"📝 Last Service Updated")
                    with col3:
                        st.caption(f"{change.get('old_value')} → {change.get('new_value')} km")
                        
                elif change_type == "last_alignment_odometer":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"🕐 {timestamp[:16]}")
                    with col2:
                        st.caption(f"📝 Last Alignment Updated")
                    with col3:
                        st.caption(f"{change.get('old_value')} → {change.get('new_value')} km")
                        
                elif change_type == "trip_added":
                    trip_data = change.get("trip_data", {})
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"🕐 {timestamp[:16]}")
                    with col2:
                        st.caption(f"🛣️ Trip Added")
                    with col3:
                        st.caption(f"{trip_data.get('km')} km | {', '.join(trip_data.get('road', []))} | {trip_data.get('date')}")
                        
                elif change_type == "report_generated":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"🕐 {timestamp[:16]}")
                    with col2:
                        st.caption(f"📊 Report Generated")
                    with col3:
                        st.caption(f"{change.get('report_type', 'unknown')} type")
                
                st.divider()
            
            # Export changes
            if st.button("📥 Export Changes Log"):
                changes_df = pd.DataFrame(changes)
                csv = changes_df.to_csv(index=False)
                st.download_button(
                    label="Download Changes Log CSV",
                    data=csv,
                    file_name=f"changes_log_{st.session_state.current_user_id}.csv",
                    mime="text/csv"
                )
    else:
        st.warning("⚠️ Load a user first to see changes log. Use the 'User Management' section above.")
