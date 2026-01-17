def calculate_risk_score(odo, last_oil, brake_age, tyre_cond, road_type, district):
    """
    Calculates a safety score from 0-100.
    """
    score = 100
    
    # 1. Brake Risk (Higher in Hill areas)
    is_hilly = district.lower() in ["kandy", "nuwara eliya", "badulla", "matale"]
    if is_hilly and brake_age > 15000:
        score -= 30  # Critical penalty for old brakes in mountains
    elif brake_age > 25000:
        score -= 20
        
    # 2. Tyre Risk
    tyre_map = {"New": 0, "Good": 5, "Fair": 20, "Low": 50}
    score -= tyre_map.get(tyre_cond, 0)
    
    # 3. Road Condition Impact
    if road_type == "Rough (Potholes/Gravel)":
        score -= 15 # Suspension stress
        
    return max(0, score)

def get_pro_report(vehicle, score, env_context, town):
    # This prompt tells the AI exactly what 'Threats' to look for
    prompt = f"""
    Act as a Safety Inspector for {vehicle} in {town}.
    Vehicle Safety Score: {score}/100.
    Environmental Threats: {env_context}.
    
    Your task:
    1. Identify 'Fatal Threats' (e.g., if score < 50 and area is Hilly, focus on Brakes/Tyres).
    2. Give a specific warning about 'Slippery Roads' or 'Engine Overheating' based on {env_context}.
    3. Suggest the next 3 specific mechanical actions.
    """
    # ... call Groq/AI ...