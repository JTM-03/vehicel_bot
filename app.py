import streamlit as st
import logic
import database
from datetime import datetime, timedelta
import pandas as pd
import json

st.set_page_config(page_title="AI Mechanic", layout="wide")

def display_formatted_report(report_data):
    """Display a formatted and colored report"""
    if isinstance(report_data, dict) and 'accident_risk' in report_data:
        # New structured format
        meta = report_data['metadata']
        risk = report_data['accident_risk']
        data = report_data['structured_data']
        
        # Title
        st.title(f" Vehicle Maintenance Report")
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
            st.subheader(" Risk Breakdown Analysis")
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
            st.subheader("Vehicle Condition Summary")
            st.markdown(report_data['vehicle_condition'])
        
        st.divider()
        
        # Weather Information
        if report_data.get('weather'):
            st.subheader("Current Weather Conditions")
            weather = report_data['weather']
            col_w1, col_w2, col_w3 = st.columns(3)
            with col_w1:
                st.metric("Temperature", f"{weather.get('temp', 'N/A')}°C")
            with col_w2:
                st.metric("Condition", weather.get('condition', 'N/A'))
            with col_w3:
                st.metric("Humidity", f"{weather.get('humidity', 'N/A')}%")
            st.caption(f" {weather.get('location', 'N/A')}")
        
        st.divider()
        
        # Safety Instructions Based on Identified Issues
        if data.get('critical_issues') or data.get('accident_risk_analysis'):
            st.subheader(" Safety Instructions While Driving")
            
            total_risk = data.get('accident_risk_analysis', {}).get('total_estimated_risk', 0)
            
            if total_risk > 70:
                st.error("⛔ **HIGH RISK - Minimize driving until critical repairs are completed**")
                st.markdown("""
                **Driving Restrictions:**
                - Avoid long-distance travel
                - Drive only on well-lit routes during daylight
                - Reduce speed significantly
                - Avoid heavy traffic areas
                - Do not drive at night
                - Have vehicle towed for repairs
                """)
            elif total_risk > 50:
                st.warning("⚠️ **MODERATE-HIGH RISK - Exercise extreme caution**")
                st.markdown("""
                **Driving Precautions:**
                - Keep emergency contacts handy
                - Drive at reduced speeds
                - Avoid highway driving
                - Maintain extra following distance
                - Stay alert and avoid distractions
                - Use hazard lights when necessary
                - Schedule repairs within 48 hours
                """)
            elif total_risk > 30:
                st.info("⚠️ **MODERATE RISK - Take precautions**")
                st.markdown("""
                **Driving Guidelines:**
                - Maintain safe speeds
                - Avoid sudden maneuvers
                - Check mirrors frequently
                - Be aware of vehicle handling changes
                - Schedule repairs within 1-2 weeks
                """)
            else:
                st.success(" **LOW RISK - Safe to drive with normal precautions**")
                st.markdown("""
                **Maintenance Reminder:**
                - Schedule regular maintenance appointments
                - Monitor vehicle condition
                - Check recommended parts replacement
                """)
            
            # Specific driving restrictions based on issues
            if data.get('critical_issues'):
                st.subheader("Specific Concerns & Driving Adjustments")
                for issue in data['critical_issues'][:3]:  # Show top 3 issues
                    if "brake" in issue.lower():
                        st.warning("🔴 **Brake Issues Detected:** Increase braking distance. Test brakes in safe area before driving.")
                    elif "steering" in issue.lower():
                        st.warning("🔴 **Steering Issues Detected:** Avoid heavy steering inputs. Drive cautiously.")
                    elif "tyre" in issue.lower() or "tire" in issue.lower():
                        st.warning("🔴 **Tire Issues Detected:** Check tire pressure immediately. Avoid high speeds.")
                    elif "engine" in issue.lower():
                        st.warning("🔴 **Engine Issues Detected:** Avoid heavy acceleration. Have it serviced urgently.")
                    elif "suspension" in issue.lower():
                        st.warning("🔴 **Suspension Issues Detected:** Avoid rough roads. Drive smoothly.")
        
        st.divider()
        
        # Critical Issues
        if data.get('critical_issues'):
            st.subheader("🔴 Critical Issues")
            for issue in data['critical_issues']:
                st.error(f"⚠️ {issue}")
        
        st.divider()
        
        # Parts to Replace
        if data.get('parts_to_replace'):
            st.subheader("Parts to Replace (Impact on Accident Risk)")
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
                        st.success(f" Replacing this part will **reduce accident risk by {risk_reduction}%**")
        
        st.divider()
        
        # Spare Parts Shops
        if data.get('spare_parts_shops'):
            st.subheader(" Spare Parts Shops Near You")
            for shop in data['spare_parts_shops']:
                with st.expander(f" {shop.get('name', 'Unknown')} - {shop.get('location', 'N/A')}"):
                    st.write(f"**Phone:** {shop.get('phone', 'N/A')}")
                    st.write(f"**Specialty:** {shop.get('specialty', 'N/A')}")
        
        st.divider()
        
        # Maintenance Tips
        if data.get('maintenance_tips'):
            st.subheader(" Maintenance Tips")
            for tip in data['maintenance_tips']:
                st.info(f"✓ {tip}")
        
        st.divider()
        
        # Road & Weather Warnings
        col1, col2 = st.columns(2)
        with col1:
            if data.get('road_specific_warnings'):
                st.subheader(" Road-Specific Warnings")
                for warning in data['road_specific_warnings']:
                    st.warning(f"⚠️ {warning}")
        
        with col2:
            if data.get('weather_advisories'):
                st.subheader(" Weather Advisories")
                for advisory in data['weather_advisories']:
                    st.warning(f"⚠️ {advisory}")
        
        st.divider()
        
        # Download Buttons
        col_csv, col_pdf = st.columns(2)
        
        with col_csv:
            csv_content = logic.generate_csv_report(report_data)
            st.download_button(
                label=" Download as CSV",
                data=csv_content,
                file_name=f"vehicle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_pdf:
            pdf_content = logic.generate_pdf_report(report_data)
            if pdf_content:
                st.download_button(
                    label=" Download as PDF",
                    data=pdf_content,
                    file_name=f"vehicle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        # Fallback for old format
        st.markdown(report_data)

# Session State for Form Data (Temporary - Not Stored)
if "vehicle_data" not in st.session_state: 
    st.session_state.vehicle_data = {"model": "", "city": "", "odo": 0, "district": "Colombo", "v_type": "Petrol/Diesel Car", "m_year": 2018, "s_odo": 0, "a_odo": 0, "tp_check": 0, "fuel_type": ""}
if "trips_data" not in st.session_state:
    st.session_state.trips_data = []
if "three_recent_trips" not in st.session_state:
    st.session_state.three_recent_trips = [{"date": datetime.now().date(), "km": 0, "road": []}]*3
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "parts_replaced" not in st.session_state:
    st.session_state.parts_replaced = []
if "parts_dates" not in st.session_state:
    st.session_state.parts_dates = {}
if "parts_mileage" not in st.session_state:
    st.session_state.parts_mileage = {}
if "additional_notes" not in st.session_state:
    st.session_state.additional_notes = ""

districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]

col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    st.image("logo.png", width=250)

st.markdown(
    """
    <div style="text-align: center; padding-top: 5px;">
        <h1 style="font-size: 46px; margin-bottom: 8px;">
            Personal Vehicle Maintenance Assistant
        </h1>
        <h3 style="font-weight: 500; letter-spacing: 2px; color: #4f8bf9;">
            Predict | Prevent | Protect
        </h3>
    </div>
    <hr style="margin-top: 15px;">
    """,
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs([" Diagnostic & Report", " AI Mechanic Chat"])

# --- TAB 1: FORM WITH TRIP DATA COLLECTION ---
with tab1:
    with st.form("main_form"):
        st.subheader(" Vehicle Information")
        st.info(" First, tell us about your vehicle")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            v_types = ["Petrol/Diesel Car", "Hybrid", "EV", "Motorbike", "Three-Wheeler"]
            v_type_default = st.session_state.vehicle_data.get("v_type", "Petrol/Diesel Car")
            v_type_index = v_types.index(v_type_default) if v_type_default in v_types else 0
            v_type = st.selectbox(
                "Vehicle Type", 
                v_types,
                index=v_type_index,
                key="v_type_select"
            )
        
        with c2:
            model = st.text_input(
                "Brand/Model", 
                placeholder="e.g. Honda Civic",
                value=st.session_state.vehicle_data.get("model", ""),
                key="model_input"
            )
        
        with c3:
            m_year = st.number_input(
                "Year", 
                1990, 
                2026, 
                int(st.session_state.vehicle_data.get("m_year", 2018)),
                key="year_input"
            )
        
        with c4:
            odo = st.number_input(
                "Odometer (km)", 
                min_value=0, 
                step=500,
                value=int(st.session_state.vehicle_data.get("odo", 0)),
                key="odo_input"
            )
        
        # Auto-detect fuel type from vehicle type (no user input needed)
        if v_type == "EV":
            fuel_type = "Electric"
        elif v_type == "Hybrid":
            fuel_type = "Hybrid"
        elif v_type == "Motorbike":
            fuel_type = "Petrol"
        elif v_type == "Three-Wheeler":
            fuel_type = "Petrol"  # Default for tuks
        else:  # Petrol/Diesel Car
            fuel_type = "Petrol"  # Default for cars
        
        st.divider()
        st.subheader(" Location")
        loc_c1, loc_c2 = st.columns(2)
        with loc_c1:
            district = st.selectbox(
                "District", 
                sorted(districts),
                index=sorted(districts).index(st.session_state.vehicle_data.get("district", "Colombo")) if st.session_state.vehicle_data.get("district") in districts else 0,
                key="district_select"
            )
        with loc_c2:
            city = st.text_input(
                "Nearest City", 
                placeholder="e.g. Maharagama",
                value=st.session_state.vehicle_data.get("city", ""),
                key="city_input"
            )
        
        st.divider()
        st.subheader(" Maintenance History")
        
        # Show different maintenance fields based on vehicle type
        if v_type in ["Motorbike", "Three-Wheeler"]:
            # For bikes and tuks: Tire pressure instead of alignment
            st.info(" Check tire pressure regularly for optimal performance and safety")
            m1, m2 = st.columns(2)
            with m1:
                s_odo = st.number_input(
                    "Last Service (km)", 
                    min_value=0, 
                    step=500,
                    value=int(st.session_state.vehicle_data.get("s_odo", 0)),
                    key="service_odo_bike"
                )
            with m2:
                tp_check = st.number_input(
                    "Last Tire Pressure Check (km)", 
                    min_value=0, 
                    step=500,
                    value=int(st.session_state.vehicle_data.get("tp_check", 0)),
                    key="tire_pressure_odo"
                )
            a_odo = tp_check  # Use tire pressure check for bikes/tuks instead of alignment
        else:
            # For cars: Regular service and alignment
            st.info(" Last service and alignment odometer readings")
            m1, m2 = st.columns(2)
            with m1:
                s_odo = st.number_input(
                    "Last Service (km)", 
                    min_value=0, 
                    step=500,
                    value=int(st.session_state.vehicle_data.get("s_odo", 0)),
                    key="service_odo_car"
                )
            with m2:
                a_odo = st.number_input(
                    "Last Alignment (km)", 
                    min_value=0, 
                    step=500,
                    value=int(st.session_state.vehicle_data.get("a_odo", 0)),
                    key="alignment_odo"
                )
        
        st.divider()
        st.subheader(" Recent Trip Data (Last 3 Trips)")
        st.info(" Tip: Enter your recent trips to get accurate maintenance predictions based on actual road conditions.")
        
        trips = []
        if st.session_state.trips_data:
            st.write("**Your stored trips:**")
            for idx, trip in enumerate(st.session_state.trips_data[-3:]):
                st.caption(f" {trip.get('date', 'N/A')} |  {trip.get('km', 0)} km |  {', '.join(trip.get('road', []))}")
            
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
        st.subheader(" Recent Parts Replacements/Changes")
        st.info(" Tell us about any parts you've replaced or changed recently to improve our recommendations.")
        
        parts_col1, parts_col2, parts_col3 = st.columns(3)
        
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
                st.write("**When were they replaced?**")
                parts_dates = {}
                for part in parts_replaced:
                    parts_dates[part] = st.date_input(
                        f"{part} - Date",
                        value=(datetime.now() - timedelta(days=30)).date(),
                        key=f"part_date_{part}"
                    )
            else:
                parts_dates = {}
        
        with parts_col3:
            if parts_replaced:
                st.write("**Odometer Reading (km) When Replaced?**")
                parts_mileage = {}
                for part in parts_replaced:
                    parts_mileage[part] = st.number_input(
                        f"{part} - Odometer Reading (km)",
                        value=odo - 5000 if odo > 5000 else 0,
                        min_value=0,
                        key=f"part_mileage_{part}",
                        help="Enter the odometer reading when this part was replaced"
                    )
            else:
                parts_mileage = {}
        
        # Additional notes
        additional_notes = st.text_area(
            "Additional Notes/Issues",
            placeholder="e.g., 'Noticed grinding sound when braking', 'Engine light is on', 'Fuel efficiency decreased'",
            key="additional_notes"
        )

        st.divider()
        col_submit, col_refresh = st.columns([3, 1])
        
        with col_submit:
            submit = st.form_submit_button(" Generate Predictive Report", use_container_width=True)
        
        with col_refresh:
            refresh = st.form_submit_button(" Refresh Form", use_container_width=True)
            if refresh:
                # Clear all form data
                st.session_state.vehicle_data = {"model": "", "city": "", "odo": 0, "district": "", "v_type": "Petrol/Diesel Car", "fuel_type": "", "m_year": 2018, "s_odo": 0, "a_odo": 0, "tp_check": 0}
                st.session_state.trips_data = []
                st.session_state.three_recent_trips = [{"date": datetime.now().date(), "km": 0, "road": []}]*3
                st.session_state.parts_replaced = []
                st.session_state.parts_dates = {}
                st.session_state.parts_mileage = {}
                st.session_state.additional_notes = ""
                st.rerun()


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
                "fuel_type": fuel_type,
                "model": model,
                "district": district,
                "city": city,
                "odo": odo,
                "m_year": m_year,
                "s_odo": s_odo,
                "a_odo": a_odo
            }
            
            # Store trip data in session
            for trip in trips:
                if trip["km"] > 0:  # Only store non-zero trips
                    st.session_state.trips_data.append(trip)
            
            report = logic.get_advanced_report(v_type, model, m_year, odo, district, city, 0, a_odo, s_odo, trips, parts_replaced, additional_notes, parts_mileage, fuel_type)
            
            # Update session state
            st.session_state.vehicle_data = vehicle_data
            
            st.success(" Diagnostic Report Generated!")
            display_formatted_report(report)

# --- TAB 2: AI MECHANIC CHATBOT ---
with tab2:
    st.subheader(" AutoSense Chatbot")
    st.info("Chat with the AI mechanic for tips and advice. Optionally upload a photo for image analysis.")
    
    # Initialize chat history for this session
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Photo upload
    with st.expander(" Upload Vehicle Photo (Optional)", expanded=False):
        photo = st.file_uploader(
            "Upload vehicle image for analysis",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="chat_photo"
        )
        if photo:
            st.image(photo, width=300, caption="Uploaded photo")
    
    # Clear chat button
    col_clear = st.columns([6, 1])[1]
    with col_clear:
        if st.button(" Clear Chat", use_container_width=True, key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Chat input - allows sending by pressing Enter
    user_query = st.chat_input(
        "Ask anything about your vehicle... (Press Enter to send)",
        key="chat_input"
    )
    
    # Process message when user sends it
    if user_query:
        # Add greeting only for the first message (when chat history is empty)
        if len(st.session_state.chat_history) == 0:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "👋 Hello! I'm your AI Mechanic. I'm here to help with any vehicle maintenance, repair, or automotive questions. What can I help you with today?"
            })
        
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Get AI response
        with st.spinner(" AI Mechanic is thinking..."):
            try:
                vehicle_context = f"{st.session_state.vehicle_data.get('model', 'Vehicle')} in {st.session_state.vehicle_data.get('city', 'Location')}"
                
                # Check if a photo is currently uploaded
                if photo:
                    # Photo analysis mode - analyze the image and provide report
                    response = logic.analyze_vision_chat(photo, user_query, vehicle_context)
                else:
                    # Text-only chat mode
                    response = logic.chat_with_mechanic(user_query, vehicle_context)
                
                # Add AI response to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)[:200]}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })
        
        # Display the updated chat
        st.rerun()
