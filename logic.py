import streamlit as st
from langchain_groq import ChatGroq
import base64
import json
from datetime import datetime
import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

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

def get_vehicle_condition_description(odo, service_odo, align_odo, m_year, parts_replaced=None):
    """Generate a human-readable description of vehicle condition"""
    km_since_service = odo - service_odo
    km_since_alignment = odo - align_odo
    current_year = 2026
    vehicle_age = current_year - m_year
    
    description = ""
    
    # Age assessment
    if vehicle_age <= 3:
        description += "🟢 **Vehicle Age:** Relatively new ("
    elif vehicle_age <= 7:
        description += "🟡 **Vehicle Age:** Mid-life ("
    else:
        description += "🔴 **Vehicle Age:** Aging vehicle ("
    description += f"{vehicle_age} years old)\n"
    
    # Service status
    if km_since_service < 5000:
        description += "🟢 **Service Status:** Recently serviced (due in ~{} km)\n".format(8000 - km_since_service)
    elif km_since_service < 8000:
        description += "🟡 **Service Status:** Service due soon (~{} km remaining)\n".format(8000 - km_since_service)
    else:
        description += "🔴 **Service Status:** OVERDUE! ({} km since last service)\n".format(km_since_service)
    
    # Alignment status
    if km_since_alignment < 5000:
        description += "🟢 **Alignment:** Recently aligned\n"
    elif km_since_alignment < 10000:
        description += "🟡 **Alignment:** May need checking soon\n"
    else:
        description += "🔴 **Alignment:** Likely overdue ({} km since last alignment)\n".format(km_since_alignment)
    
    # Parts history
    if parts_replaced:
        description += f"✅ **Recent Maintenance:** {len(parts_replaced)} part(s) recently replaced\n"
    else:
        description += "⚠️ **Recent Maintenance:** No recent maintenance recorded\n"
    
    # Overall assessment
    if km_since_service < 8000 and km_since_alignment < 10000 and vehicle_age <= 7:
        description += "\n**Overall:** Vehicle in GOOD condition. Keep up regular maintenance."
    elif km_since_service < 8000 and vehicle_age <= 10:
        description += "\n**Overall:** Vehicle in FAIR condition. Schedule alignment and regular checks."
    else:
        description += "\n**Overall:** Vehicle needs ATTENTION. Schedule maintenance immediately."
    
    return description

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
    Act as a Sri Lankan Professional Automobile Mechanic (2026) creating a COMPREHENSIVE RISK ASSESSMENT.
    
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
    
    ⚠️ CRITICAL TASK: Analyze ALL vehicle information and identify which parts CRITICALLY affect accident risk percentage.
    
    ANALYZE:
    1. How many critical parts (brakes, tires, steering, suspension) need replacement?
    2. Each critical part missing/worn increases accident risk. Estimate the risk increase percentage.
    3. Show which parts are SAFETY CRITICAL (brake failure = 40%+ risk increase, tire failure = 35%+ risk increase, steering = 30%+ risk, etc.)
    4. Calculate total accident risk based on: Vehicle Age + Service Status + Critical Parts Needed + Weather + Road Conditions
    5. If service is OVERDUE by significant km, that increases risk
    6. If recent parts were REPLACED, that REDUCES risk for those components
    
    Provide ONLY a structured JSON response (no markdown, no extra text):
    {{
        "critical_issues": ["issue1", "issue2"],
        "accident_risk_analysis": {{
            "base_risk": 30,
            "critical_parts_impact": [
                {{"part": "Brake Pads", "risk_increase": 15, "reason": "Heavy wear detected, reduced braking efficiency increases accident risk"}},
                {{"part": "Tires", "risk_increase": 12, "reason": "Tread wear high, grip compromised on wet roads"}}
            ],
            "service_overdue_impact": 10,
            "weather_impact": 5,
            "road_conditions_impact": 8,
            "recently_replaced_reduction": -5,
            "total_estimated_risk": 75
        }},
        "parts_to_replace": [
            {{"name": "part name", "urgency": "CRITICAL/HIGH/MODERATE", "estimated_cost_lkr": 5000, "why": "reason", "risk_reduction_if_replaced": 15}},
        ],
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
            "accident_risk_analysis": {
                "base_risk": 0,
                "critical_parts_impact": [],
                "total_estimated_risk": 0
            },
            "parts_to_replace": [],
            "spare_parts_shops": [],
            "maintenance_tips": [],
            "road_specific_warnings": [],
            "weather_advisories": []
        }
    
    # Get vehicle condition description
    vehicle_condition_desc = get_vehicle_condition_description(odo, service_odo, align_odo, m_year, parts_replaced)
    
    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "vehicle": f"{m_year} {model}",
            "location": f"{city}, {district}",
            "current_odometer": odo
        },
        "vehicle_condition": vehicle_condition_desc,
        "accident_risk": accident_risk,
        "weather": weather,
        "road_conditions": road_conditions,
        "structured_data": structured_data
    }

def get_advanced_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, service_odo, trips, parts_replaced=None, additional_notes=None):
    """Legacy function - returns structured report"""
    return get_structured_report(v_type, model, m_year, odo, district, city, tyre_odo, align_odo, service_odo, trips, parts_replaced, additional_notes)

def analyze_vision_chat(image_file, user_query, vehicle_context):
    """Analyze vehicle image using vision AI"""
    try:
        import base64
        import os
        import tempfile
        from groq import Groq
        
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            return "❌ API key not configured. Please set GROQ_API_KEY."
        
        # Read and prepare image
        image_data = image_file.read()
        image_file.seek(0)
        
        # Create Groq client
        client = Groq(api_key=api_key)
        
        # Encode to base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # Detect image type
        filename = image_file.name.lower()
        if filename.endswith('.png'):
            mime_type = "image/png"
        elif filename.endswith(('.jpg', '.jpeg')):
            mime_type = "image/jpeg"
        else:
            mime_type = "image/jpeg"
        
        # Prepare the message with proper structure for vision model
        message = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": f"""You are an expert Sri Lankan automotive mechanic (2026). Analyze this vehicle photo.

VEHICLE: {vehicle_context}
QUESTION: {user_query}

Provide analysis in this format:
• **What I see:** [part/component identification]
• **Condition:** [Good/Fair/Poor]
• **Issues Found:** [specific problems if any]
• **Maintenance Required:** [what needs to be done]
• **Est. Cost (LKR):** [price with 18% VAT + 2.5% SSCL]
• **Urgency:** [Immediate/Soon/Preventive/None]

Be brief, practical, and specific."""
                        }
                    ]
                }
            ],
            max_tokens=1024,
            temperature=0.3
        )
        
        return message.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e)
        if "vision" in error_msg.lower() or "image" in error_msg.lower():
            return f"""⚠️ Image Analysis Error

The image couldn't be processed. This can happen if:
- Image is too small or blurry
- Image format is unsupported
- Image quality is very poor

💡 Try uploading a clearer, well-lit photo of the vehicle part."""
        elif "api" in error_msg.lower():
            return "❌ API Connection Error: Check your GROQ API key and internet connection."
        else:
            return f"❌ Analysis Error: {error_msg[:100]}"

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

def generate_pdf_report(report_data):
    """Generate PDF export of the report"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            alignment=1
        )
        story.append(Paragraph("🔧 Vehicle Maintenance Report", title_style))
        
        # Metadata
        meta = report_data['metadata']
        meta_data = [
            ['Vehicle:', f"{meta['vehicle']}"],
            ['Location:', f"{meta['location']}"],
            ['Odometer:', f"{meta['current_odometer']} km"],
            ['Generated:', meta['generated_at'][:10]]
        ]
        meta_table = Table(meta_data, colWidths=[1.5*inch, 3.5*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Assessment
        story.append(Paragraph("⚠️ Accident Risk Assessment", styles['Heading2']))
        risk = report_data['accident_risk']
        risk_data = [
            ['Risk Level:', risk['level'], 'Score:', f"{risk['score']}/100"]
        ]
        risk_table = Table(risk_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff3cd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(risk_table)
        
        # Risk Factors
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Risk Factors:", styles['Heading3']))
        for factor in risk['factors']:
            story.append(Paragraph(f"• {factor}", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Critical Issues
        data = report_data['structured_data']
        if data.get('critical_issues'):
            story.append(Paragraph("🔴 Critical Issues", styles['Heading2']))
            for issue in data['critical_issues']:
                story.append(Paragraph(f"⚠️ {issue}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Parts to Replace
        if data.get('parts_to_replace'):
            story.append(Paragraph("🔧 Parts to Replace", styles['Heading2']))
            parts_data = [['Part', 'Urgency', 'Cost (LKR)', 'Reason']]
            for part in data['parts_to_replace']:
                parts_data.append([
                    part.get('name', 'Unknown')[:20],
                    part.get('urgency', 'N/A'),
                    str(part.get('estimated_cost_lkr', 0)),
                    part.get('why', 'N/A')[:30]
                ])
            
            parts_table = Table(parts_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.6*inch])
            parts_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6b6b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffe6e6')])
            ]))
            story.append(parts_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Next Service
        service = data.get('next_service', {})
        story.append(Paragraph("📅 Next Service Schedule", styles['Heading2']))
        service_data = [
            ['When:', service.get('when', 'N/A')],
            ['Estimated Cost:', f"LKR {service.get('estimated_cost_lkr', 0):,}"],
            ['Includes:', ', '.join(service.get('what_includes', []))]
        ]
        service_table = Table(service_data, colWidths=[2*inch, 3*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(service_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Maintenance Tips
        if data.get('maintenance_tips'):
            story.append(Paragraph("💡 Maintenance Tips", styles['Heading2']))
            for tip in data['maintenance_tips'][:5]:  # Limit to 5 tips
                story.append(Paragraph(f"✓ {tip}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        return None