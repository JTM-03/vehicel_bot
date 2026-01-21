import streamlit as st
from langchain_groq import ChatGroq
import base64
import json
from datetime import datetime
import requests

def get_weather_data(city):
    """Get current weather for the city"""
    try:
        # Free weather API
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            return {
                "temp": current['temp_C'],
                "condition": current['weatherDesc'][0]['value'],
                "humidity": current['humidity'],
                "wind_speed": current['windspeedKmph']
            }
    except:
        pass
    return None

def calculate_accident_risk(vehicle_condition, weather, road_conditions, parts_replaced=None):
    """Calculate accident risk based on multiple factors"""
    risk_score = 0
    risk_factors = []
    
    # Vehicle condition (0-40 points)
    if vehicle_condition.get('service_overdue'):
        risk_score += 15
        risk_factors.append("⚠️ Service overdue")
    if vehicle_condition.get('tyre_wear_high'):
        risk_score += 12
        risk_factors.append("⚠️ High tyre wear")
    if vehicle_condition.get('brake_wear_high'):
        risk_score += 13
        risk_factors.append("⚠️ High brake wear")
    
    # Parts replaced recently (reduces risk for those parts)
    if parts_replaced:
        for part in parts_replaced:
            if 'Tyre' in part or 'Tyres' in part:
                risk_score = max(0, risk_score - 8)  # Recently replaced tires = safer
                risk_factors.append("✅ Tyres recently replaced")
            elif 'Brake' in part:
                risk_score = max(0, risk_score - 8)
                risk_factors.append("✅ Brakes recently serviced")
            elif 'Battery' in part:
                risk_score = max(0, risk_score - 3)
                risk_factors.append("✅ Battery recently replaced")
    
    # Weather conditions (0-30 points)
    if weather:
        if 'rain' in weather['condition'].lower():
            risk_score += 10
            risk_factors.append("🌧️ Rainy conditions")
        if int(weather['wind_speed']) > 40:
            risk_score += 10
            risk_factors.append("💨 High winds")
    
    # Road conditions (0-30 points)
    if 'Mountain' in road_conditions:
        risk_score += 12
        risk_factors.append("⛰️ Mountain roads")
    if 'Rough' in road_conditions:
        risk_score += 10
        risk_factors.append("🛣️ Rough roads")
    if 'City' in road_conditions:
        risk_score += 5
        risk_factors.append("🏙️ City traffic")
    
    # Ensure score is between 0-100
    risk_score = max(0, min(100, risk_score))
    
    # Determine risk level
    if risk_score >= 60:
        risk_level = "🔴 CRITICAL"
        color = "#ff4444"
    elif risk_score >= 40:
        risk_level = "🟠 HIGH"
        color = "#ff9900"
    elif risk_score >= 20:
        risk_level = "🟡 MODERATE"
        color = "#ffcc00"
    else:
        risk_level = "🟢 LOW"
        color = "#00cc00"
    
    return {
        "score": risk_score,
        "level": risk_level,
        "color": color,
        "factors": risk_factors
    }

def get_structured_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, service_odo, trips, parts_replaced=None, additional_notes=None):
    """Generate structured report with sections"""
    api_key = st.secrets.get("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
    
    # Get weather data
    weather = get_weather_data(city)
    
    # Extract road conditions from trips
    road_conditions = []
    for trip in trips:
        road_conditions.extend(trip.get("road", []))
    road_conditions = list(set(road_conditions))
    
    # Calculate service intervals
    km_since_service = odo - service_odo
    km_since_alignment = odo - align_odo
    service_due = km_since_service >= 8000
    alignment_due = km_since_alignment >= 10000
    
    # Vehicle condition assessment
    vehicle_condition = {
        'service_overdue': service_due,
        'tyre_wear_high': km_since_service > 6000,
        'brake_wear_high': km_since_service > 7000
    }
    
    # Calculate accident risk
    accident_risk = calculate_accident_risk(vehicle_condition, weather, road_conditions, parts_replaced)
    
    # Format trip data
    trips_summary = ""
    for i, trip in enumerate(trips, 1):
        date_str = trip.get("date", "Unknown")
        km = trip.get("km", 0)
        roads = ', '.join(trip.get("road", [])) or "Not specified"
        trips_summary += f"Trip {i} ({date_str}): {km}km on {roads} roads\n"
    
    # Format parts replacement data
    parts_info = ""
    if parts_replaced:
        parts_info = "RECENT PARTS REPLACED:\n"
        for part in parts_replaced:
            parts_info += f"  - {part}\n"
    
    # Get detailed recommendations from LLM
    prompt = f"""
    Act as a Sri Lankan Professional Automobile Mechanic (2026).
    
    VEHICLE DETAILS:
    - Model: {m_year} {model} ({v_type})
    - Current Odometer: {odo}km
    - Last Service: {service_odo}km (km since service: {km_since_service}km)
    - Last Alignment: {align_odo}km (km since alignment: {km_since_alignment}km)
    - Location: {city}, {district}
    
    RECENT TRIPS:
    {trips_summary}
    
    {parts_info}
    
    USER REPORTED ISSUES:
    {additional_notes if additional_notes else 'No issues reported'}
    
    WEATHER (Today):
    - Temperature: {weather['temp'] if weather else 'N/A'}°C
    - Condition: {weather['condition'] if weather else 'N/A'}
    - Humidity: {weather['humidity'] if weather else 'N/A'}%
    
    ROAD CONDITIONS (from recent trips): {', '.join(road_conditions) if road_conditions else 'Unknown'}
    
    Based on the vehicle condition, recent parts replaced, user-reported issues, weather, and road conditions, provide ONLY a structured JSON response (no markdown, no extra text) with these exact fields:
    {{
        "critical_issues": ["issue1", "issue2"],
        "parts_to_replace": [
            {{"name": "part name", "urgency": "CRITICAL/HIGH/MODERATE", "estimated_cost_lkr": 5000, "why": "reason"}},
        ],
        "next_service": {{
            "when": "in X km / on DATE",
            "estimated_cost_lkr": 15000,
            "what_includes": ["service", "parts"]
        }},
        "spare_parts_shops": [
            {{"name": "Shop Name", "location": "City/Area", "phone": "0XX-XXXXXXX", "specialty": "type"}},
        ],
        "maintenance_tips": ["tip1", "tip2"],
        "road_specific_warnings": ["warning1"],
        "weather_advisories": ["advisory1"]
    }}
    """
    
    try:
        response = llm.invoke(prompt).content
        # Clean response to extract JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        structured_data = json.loads(response)
    except:
        structured_data = {
            "critical_issues": ["Unable to connect to AI service"],
            "parts_to_replace": [],
            "next_service": {"when": "Consult a mechanic", "estimated_cost_lkr": 0},
            "spare_parts_shops": [],
            "maintenance_tips": [],
            "road_specific_warnings": [],
            "weather_advisories": []
        }
    
    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "vehicle": f"{m_year} {model}",
            "location": f"{city}, {district}",
            "current_odometer": odo
        },
        "accident_risk": accident_risk,
        "weather": weather,
        "road_conditions": road_conditions,
        "structured_data": structured_data
    }

def get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, service_odo, trips, parts_replaced=None, additional_notes=None):
    """Legacy function - returns structured report"""
    return get_structured_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, service_odo, trips, parts_replaced, additional_notes)

def analyze_vision_chat(image_file, user_query, vehicle_context):
    api_key = st.secrets.get("GROQ_API_KEY")
    vision_llm = ChatGroq(model="llama-3.2-11b-vision-preview", groq_api_key=api_key)
    image_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    prompt = [
        {"role": "user", "content": [
            {"type": "text", "text": f"Context: {vehicle_context}. Query: {user_query}. Analyze image for maintenance/errors. Include 2026 LKR costs with 18% VAT and 2.5% SSCL."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]}
    ]
    try:
        return vision_llm.invoke(prompt).content
    except Exception as e: return "Vision system error. Please ensure the image is clear."

def generate_csv_report(report_data):
    """Generate CSV export of the report"""
    csv_content = "Vehicle Maintenance Report\n"
    csv_content += f"Generated: {report_data['metadata']['generated_at']}\n"
    csv_content += f"Vehicle: {report_data['metadata']['vehicle']}\n"
    csv_content += f"Location: {report_data['metadata']['location']}\n"
    csv_content += f"Odometer: {report_data['metadata']['current_odometer']} km\n\n"
    
    csv_content += f"ACCIDENT RISK: {report_data['accident_risk']['level']}\n"
    csv_content += f"Risk Score: {report_data['accident_risk']['score']}/100\n"
    csv_content += "Risk Factors:\n"
    for factor in report_data['accident_risk']['factors']:
        csv_content += f"  - {factor}\n"
    csv_content += "\n"
    
    data = report_data['structured_data']
    
    csv_content += "CRITICAL ISSUES:\n"
    for issue in data.get('critical_issues', []):
        csv_content += f"  - {issue}\n"
    csv_content += "\n"
    
    csv_content += "PARTS TO REPLACE:\n"
    for part in data.get('parts_to_replace', []):
        csv_content += f"  - {part.get('name', 'Unknown')}: {part.get('estimated_cost_lkr', 0)} LKR ({part.get('urgency', 'N/A')})\n"
        csv_content += f"    Why: {part.get('why', 'N/A')}\n"
    csv_content += "\n"
    
    csv_content += "NEXT SERVICE:\n"
    service = data.get('next_service', {})
    csv_content += f"  When: {service.get('when', 'N/A')}\n"
    csv_content += f"  Cost: {service.get('estimated_cost_lkr', 0)} LKR\n"
    csv_content += f"  Includes: {', '.join(service.get('what_includes', []))}\n\n"
    
    csv_content += "MAINTENANCE TIPS:\n"
    for tip in data.get('maintenance_tips', []):
        csv_content += f"  - {tip}\n"
    csv_content += "\n"
    
    csv_content += "SPARE PARTS SHOPS:\n"
    for shop in data.get('spare_parts_shops', []):
        csv_content += f"  - {shop.get('name', 'Unknown')}\n"
        csv_content += f"    Location: {shop.get('location', 'N/A')}\n"
        csv_content += f"    Phone: {shop.get('phone', 'N/A')}\n"
        csv_content += f"    Specialty: {shop.get('specialty', 'N/A')}\n"
    
    return csv_content