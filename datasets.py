"""
Dataset Handler Module
Loads and manages maintenance schedules, OBD codes, and specialized vehicle data
"""

import pandas as pd
import os
import streamlit as st
from pathlib import Path

class DatasetHandler:
    """Load and cache datasets for vehicle maintenance and diagnostics"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.maintenance_df = None
        self.obd_codes_df = None
        self.bike_maintenance = None
        self.tuk_maintenance = None
        
    @st.cache_data
    def load_maintenance_schedule(_self):
        """Load maintenance schedule dataset"""
        try:
            path = _self.base_path / "maintain_schdule.csv"
            df = pd.read_csv(path)
            return df
        except Exception as e:
            st.warning(f"Could not load maintenance schedule: {e}")
            return None
    
    @st.cache_data
    def load_obd_codes(_self):
        """Load OBD trouble codes dataset"""
        try:
            path = _self.base_path / "obd-trouble-codes.csv"
            df = pd.read_csv(path, header=None, names=["Code", "Description"])
            return df
        except Exception as e:
            st.warning(f"Could not load OBD codes: {e}")
            return None
    
    def get_maintenance_for_odometer(self, current_odometer, last_service_odo, vehicle_type="Car"):
        """
        Get maintenance recommendations based on odometer readings
        Uses maintenance schedule dataset
        """
        try:
            df = self.load_maintenance_schedule()
            if df is None:
                return []
            
            km_since_service = current_odometer - last_service_odo
            
            # Get relevant maintenance records from dataset
            recommendations = []
            
            if km_since_service >= 5000:
                recommendations.append({
                    "part": "Engine Oil",
                    "action": "Change",
                    "urgency": "CRITICAL" if km_since_service >= 8000 else "HIGH",
                    "km_until_due": max(0, 8000 - km_since_service)
                })
            
            if km_since_service >= 10000:
                recommendations.append({
                    "part": "Air Filter",
                    "action": "Replace",
                    "urgency": "HIGH",
                    "km_until_due": 0
                })
            
            if km_since_service >= 15000:
                recommendations.append({
                    "part": "Cabin Air Filter",
                    "action": "Replace",
                    "urgency": "MEDIUM",
                    "km_until_due": 0
                })
            
            return recommendations
        except Exception as e:
            st.error(f"Error getting maintenance: {e}")
            return []
    
    def get_obd_description(self, trouble_code):
        """
        Get OBD trouble code description from dataset
        Handles codes like P0100, C1234, etc.
        """
        try:
            df = self.load_obd_codes()
            if df is None:
                return f"OBD Code: {trouble_code} (Description not found)"
            
            # Search for the code
            code_upper = trouble_code.upper()
            match = df[df['Code'].str.strip().str.upper() == code_upper]
            
            if not match.empty:
                description = match.iloc[0]['Description']
                return f"**{trouble_code}**: {description}"
            else:
                return f"OBD Code: {trouble_code} (Not found in database)"
                
        except Exception as e:
            return f"Error looking up code {trouble_code}: {e}"
    
    def get_bike_maintenance(self):
        """Get maintenance schedule for motorbikes"""
        try:
            bike_data = {
                "Mileage": [3000, 5000, 10000, 15000, 20000],
                "Actions": [
                    "Change engine oil (1L), check spark plugs",
                    "Lubricate chain, inspect brake shoes",
                    "Clean/replace air filter, check fuel filter",
                    "Replace chain sprocket kit, check bearings",
                    "Inspect suspension, check wheel alignment"
                ],
                "Urgency": ["CRITICAL", "HIGH", "HIGH", "HIGH", "MEDIUM"],
                "Estimated_Cost_LKR": [2800, 3500, 4200, 8500, 5000]
            }
            return pd.DataFrame(bike_data)
        except Exception as e:
            st.warning(f"Could not load bike maintenance: {e}")
            return None
    
    def get_tuk_maintenance(self):
        """Get maintenance schedule for three-wheelers"""
        try:
            tuk_data = {
                "Mileage": [1000, 5000, 10000, 25000, 50000],
                "Actions": [
                    "Grease all nipples, check clutch",
                    "Change engine oil, inspect CV joint",
                    "Check brake system, inspect canvas hood",
                    "Replace brake shoes, inspect axle bearings",
                    "Full overhaul - engine, transmission, suspension"
                ],
                "Urgency": ["CRITICAL", "CRITICAL", "HIGH", "HIGH", "MEDIUM"],
                "Estimated_Cost_LKR": [500, 3200, 5000, 12500, 35000]
            }
            return pd.DataFrame(tuk_data)
        except Exception as e:
            st.warning(f"Could not load tuk maintenance: {e}")
            return None
    
    def get_bike_parts_info(self):
        """Get bike parts pricing and information"""
        parts = {
            "Engine Oil (1L)": {"Price_LKR": 2800, "Interval_km": 3000, "Urgency": "CRITICAL"},
            "Air Filter": {"Price_LKR": 1200, "Interval_km": 10000, "Urgency": "MEDIUM"},
            "Spark Plug": {"Price_LKR": 850, "Interval_km": 5000, "Urgency": "HIGH"},
            "Chain Sprocket Kit": {"Price_LKR": 8500, "Interval_km": 15000, "Urgency": "HIGH"},
            "Brake Shoes (Rear)": {"Price_LKR": 1500, "Interval_km": 10000, "Urgency": "HIGH"}
        }
        return parts
    
    def get_tuk_parts_info(self):
        """Get three-wheeler parts pricing and information"""
        parts = {
            "Engine Oil (RE)": {"Price_LKR": 3200, "Interval_km": 5000, "Urgency": "CRITICAL"},
            "CV Joint (Axle)": {"Price_LKR": 12500, "Interval_km": 25000, "Urgency": "HIGH"},
            "Canvas Hood": {"Price_LKR": 18000, "Interval_km": 50000, "Urgency": "LOW"},
            "Clutch Cable": {"Price_LKR": 1200, "Interval_km": 10000, "Urgency": "MEDIUM"},
            "Grease Nipple Service": {"Price_LKR": 500, "Interval_km": 1000, "Urgency": "CRITICAL"}
        }
        return parts
    
    def get_maintenance_recommendations(self, vehicle_type, current_odo, service_odo):
        """
        Get maintenance recommendations based on vehicle type and odometer
        Returns data from dataset instead of AI generation
        """
        km_since_service = current_odo - service_odo
        recommendations = []
        
        if vehicle_type in ["Motorbike", "Bike", "Motorcycle"]:
            parts_info = self.get_bike_parts_info()
            for part_name, info in parts_info.items():
                if km_since_service >= info["Interval_km"]:
                    recommendations.append({
                        "name": part_name,
                        "urgency": info["Urgency"],
                        "estimated_cost_lkr": info["Price_LKR"],
                        "why": f"Service interval of {info['Interval_km']} km exceeded",
                        "risk_reduction_if_replaced": 5
                    })
        
        elif vehicle_type in ["Three-Wheeler", "Tuk", "Auto"]:
            parts_info = self.get_tuk_parts_info()
            for part_name, info in parts_info.items():
                if km_since_service >= info["Interval_km"]:
                    recommendations.append({
                        "name": part_name,
                        "urgency": info["Urgency"],
                        "estimated_cost_lkr": info["Price_LKR"],
                        "why": f"Service interval of {info['Interval_km']} km exceeded",
                        "risk_reduction_if_replaced": 5
                    })
        
        return recommendations

# Initialize global handler
dataset_handler = DatasetHandler()
