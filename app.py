import streamlit as st
import logic
import database
from datetime import datetime, timedelta
import pandas as pd
import json

st.set_page_config(page_title="SL AI Mechanic 2026", layout="wide")

def display_formatted_report(report_data):
    """Display a formatted and colored report"""
    if isinstance(report_data, dict) and 'accident_risk' in report_data:
        # New structured format
        meta = report_data['metadata']
        risk = report_data['accident_risk']
        data = report_data['structured_data']
        
        # Title
        st.title(f"🔧 Vehicle Maintenance Report")
        st.markdown(f"**Vehicle:** {meta['vehicle']} | **Location:** {meta['location']} | **Odometer:** {meta['current_odometer']} km")
        st.divider()
        
        # Accident Risk Section with detailed analysis
        st.subheader("⚠️ Accident Risk Assessment")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.metric("Risk Level", risk['level'], risk['score'])
        with col2:
            for factor in risk['factors']:
                st.caption(factor)
        
        # Show detailed risk breakdown if available
        if data.get('accident_risk_analysis'):
            st.divider()
            st.subheader("📊 Risk Breakdown Analysis")
            analysis = data['accident_risk_analysis']
            
            # Show total risk
            total_risk = analysis.get('total_estimated_risk', 0)
            st.metric("Total Accident Risk", f"{total_risk}%")
            
            # Show component breakdown
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Base Risk", f"{analysis.get('base_risk', 0)}%")
            with col_b:
                parts_impact = sum([p.get('risk_increase', 0) for p in analysis.get('critical_parts_impact', [])])
                st.metric("Critical Parts Impact", f"+{parts_impact}%")
            with col_c:
                service_impact = analysis.get('service_overdue_impact', 0)
                st.metric("Service Overdue", f"+{service_impact}%")
            
            # Show which critical parts affect risk
            if analysis.get('critical_parts_impact'):
                st.write("**🔴 Parts Affecting Accident Risk:**")
                for part in analysis['critical_parts_impact']:
                    impact = part.get('risk_increase', 0)
                    reason = part.get('reason', 'Impact on safety')
                    st.warning(f"**{part.get('part')}** → +{impact}% risk ({reason})")
        
        # Vehicle Condition Description
        if 'vehicle_condition' in report_data:
            st.divider()
            st.subheader("🚗 Vehicle Condition Summary")
            st.markdown(report_data['vehicle_condition'])
        
        st.divider()
        
        # Critical Issues
        if data.get('critical_issues'):
            st.subheader("🔴 Critical Issues")
            for issue in data['critical_issues']:
                st.error(f"⚠️ {issue}")
        
        st.divider()
        
        # Parts to Replace
        if data.get('parts_to_replace'):
            st.subheader("🔧 Parts to Replace (Impact on Accident Risk)")
            for part in data['parts_to_replace']:
                urgency = part.get('urgency', 'MODERATE')
                if urgency == 'CRITICAL':
                    color = "🔴"
                elif urgency == 'HIGH':
                    color = "🟠"
                else:
                    color = "🟡"
                
                risk_reduction = part.get('risk_reduction_if_replaced', 0)
                with st.expander(f"{color} {part.get('name', 'Unknown')} - {part.get('estimated_cost_lkr', 0)} LKR"):
                    st.write(f"**Why:** {part.get('why', 'N/A')}")
                    st.write(f"**Urgency:** {urgency}")
                    st.write(f"**Estimated Cost:** LKR {part.get('estimated_cost_lkr', 0):,}")
                    if risk_reduction > 0:
                        st.success(f"✅ Replacing this part will **reduce accident risk by {risk_reduction}%**")
        
        st.divider()
        
        # Spare Parts Shops
        if data.get('spare_parts_shops'):
            st.subheader("🏪 Spare Parts Shops Near You")
            for shop in data['spare_parts_shops']:
                with st.expander(f"📍 {shop.get('name', 'Unknown')} - {shop.get('location', 'N/A')}"):
                    st.write(f"**Phone:** {shop.get('phone', 'N/A')}")
                    st.write(f"**Specialty:** {shop.get('specialty', 'N/A')}")
        
        st.divider()
        
        # Maintenance Tips
        if data.get('maintenance_tips'):
            st.subheader("💡 Maintenance Tips")
            for tip in data['maintenance_tips']:
                st.info(f"✓ {tip}")
        
        st.divider()
        
        # Road & Weather Warnings
        col1, col2 = st.columns(2)
        with col1:
            if data.get('road_specific_warnings'):
                st.subheader("🛣️ Road-Specific Warnings")
                for warning in data['road_specific_warnings']:
                    st.warning(f"⚠️ {warning}")
        
        with col2:
            if data.get('weather_advisories'):
                st.subheader("🌤️ Weather Advisories")
                for advisory in data['weather_advisories']:
                    st.warning(f"⚠️ {advisory}")
        
        st.divider()
        
        # Download Buttons
        col_csv, col_pdf = st.columns(2)
        
        with col_csv:
            csv_content = logic.generate_csv_report(report_data)
            st.download_button(
                label="📊 Download as CSV",
                data=csv_content,
                file_name=f"vehicle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_pdf:
            pdf_content = logic.generate_pdf_report(report_data)
            if pdf_content:
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_content,
                    file_name=f"vehicle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        # Fallback for old format
        st.markdown(report_data)

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

# Data Management - Load past entries from history
manage_col1, manage_col2 = st.columns(2)

with manage_col1:
    st.subheader("📂 Quick Actions")
    col_new, col_reload = st.columns(2)
    
    with col_new:
        if st.button("🆕 New Entry", use_container_width=True):
            st.session_state.vehicle_data = {"model": "", "city": "", "odo": 0, "district": "", "v_type": "", "m_year": 2018}
            st.session_state.trips_data = []
            st.session_state.history_log = []
            st.session_state.changes_log = []
            st.info("✓ Ready for new vehicle entry")
            st.rerun()
    
    with col_reload:
        if st.button("🔄 Reload Last", use_container_width=True):
            if st.session_state.history_log:
                st.success("✓ Last entry loaded from history")
            else:
                st.info("No history found yet")

with manage_col2:
    st.subheader("📋 Reload Past Entry")
    if st.session_state.history_log:
        # Get unique vehicle entries from history (reverse order to show latest first)
        unique_entries = {}
        for entry in reversed(st.session_state.history_log):
            key = f"{entry.get('model', 'Unknown')} - {entry.get('date', '')}"
            if key not in unique_entries:
                unique_entries[key] = entry
        
        selected_entry = st.selectbox(
            "Select past entry to reload",
            list(unique_entries.keys()),
            label_visibility="collapsed"
        )
        
        if st.button("📂 Load Selected", use_container_width=True):
            if selected_entry:
                st.info(f"✓ Loaded: {selected_entry}")
    else:
        st.info("📌 No past entries. Start with 'New Entry' above.")

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

tab1, tab2, tab3, tab4 = st.tabs(["📋 Manual Diagnostic", "🤳 Photo Chat", "📜 History", "📝 Changes Log"])

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
        st.subheader("🔄 Recent Parts Replacements/Changes")
        st.info("📌 Tell us about any parts you've replaced or changed recently to improve our recommendations.")
        
        parts_col1, parts_col2 = st.columns(2)
        
        with parts_col1:
            parts_replaced = st.multiselect(
                "Parts Recently Replaced/Changed",
                ["Engine Oil", "Air Filter", "Cabin Filter", "Spark Plugs", "Battery", 
                 "Brake Pads", "Brake Fluid", "Tyres", "Alignment", "Suspension", 
                 "Exhaust", "Radiator Hose", "Water Pump", "Alternator", "Starter Motor",
                 "Transmission Fluid", "Power Steering Fluid", "Clutch Plate", "Other"],
                key="parts_replaced"
            )
        
        with parts_col2:
            if parts_replaced:
                parts_dates = {}
                st.write("**When were they replaced?**")
                for part in parts_replaced:
                    parts_dates[part] = st.date_input(
                        f"{part}",
                        value=(datetime.now() - timedelta(days=30)).date(),
                        key=f"part_date_{part}"
                    )
            else:
                parts_dates = {}
        
        # Additional notes
        additional_notes = st.text_area(
            "Additional Notes/Issues",
            placeholder="e.g., 'Noticed grinding sound when braking', 'Engine light is on', 'Fuel efficiency decreased'",
            key="additional_notes"
        )

        st.divider()
        submit = st.form_submit_button("🔍 Generate Predictive Report", use_container_width=True)


    # Report generation is handled below with better validation

    if submit:
        if not model:
            st.error("❌ Please enter vehicle model")
        elif not any([t["km"] > 0 for t in trips]):
            st.error("❌ Please enter at least one trip distance")
        else:
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
            
            # Generate user ID from model + city (backend identification)
            user_id = database.generate_user_id(model, city)
            
            # Store trip data
            for trip in trips:
                if trip["km"] > 0:  # Only store non-zero trips
                    st.session_state.trips_data.append(trip)
            
            report = logic.get_advanced_report(v_type, model, m_year, odo, district, city, 0, a_odo, s_odo, trips, parts_replaced, additional_notes)
            
            # Store in session history (not in database)
            st.session_state.history_log.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                "model": model, 
                "type": "Diagnostic", 
                "content": report
            })
            
            # Update session state
            st.session_state.vehicle_data = vehicle_data
            
            st.success("✅ Diagnostic Report Generated!")
            display_formatted_report(report)

# --- TAB 2: PHOTO CHAT ---
with tab2:
    st.subheader("🤳 AI Photo Mechanic")
    st.info("📸 Upload a photo and ask the bot about errors or maintenance.")
    
    col_photo, col_question = st.columns([1, 1])
    
    with col_photo:
        st.write("**Upload Image**")
        photo = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    with col_question:
        st.write("**Your Question**")
        query = st.text_input(
            "Ask about the photo",
            placeholder="e.g., Is this brake pad worn out? What maintenance is needed?",
            label_visibility="collapsed"
        )
    
    if photo and query:
        st.image(photo, width=300, caption="Uploaded Image")
        
        with st.spinner("🔍 Analyzing image..."):
            try:
                context = f"{st.session_state.vehicle_data.get('model', 'Vehicle')} in {st.session_state.vehicle_data.get('city', 'Location')}"
                ans = logic.analyze_vision_chat(photo, query, context)
                
                st.success("✅ Analysis Complete")
                st.markdown(ans)
                
                st.session_state.history_log.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                    "model": st.session_state.vehicle_data.get('model', 'Vehicle'), 
                    "type": "Photo Analysis", 
                    "content": ans
                })
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("💡 Tip: Make sure the image is clear and shows the vehicle part clearly.")
    elif photo:
        st.image(photo, width=300, caption="Uploaded Image")
        st.info("👆 Please ask a question about the photo above")
    else:
        st.info("👆 Start by uploading a clear photo of your vehicle or the part you're concerned about")

# --- TAB 3: HISTORY ---
with tab3:
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

# --- TAB 4: CHANGES LOG ---
with tab4:
    st.subheader("📝 Session Changes & Actions Log")
    
    if not st.session_state.changes_log:
        st.info("📌 No changes recorded yet in this session. Make updates to track them here.")
    else:
        st.write(f"**Total Actions:** {len(st.session_state.changes_log)}")
        st.divider()
        
        # Display changes in reverse order (newest first)
        for change in reversed(st.session_state.changes_log):
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
                    st.caption(f"{change.get('report_type', 'Diagnostic')} type")
            
            st.divider()
        
        st.info("💡 Changes are saved in session only. Generate a new report to add it to history.")
