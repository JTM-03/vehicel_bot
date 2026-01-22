import pandas as pd
import os

if not os.path.exists('data'):
    os.makedirs('data')

# --- 1. MOTORBIKE RULES (e.g., TVS, Yamaha, Bajaj) ---
bike_data = {
    "Vehicle_Type": ["Motor Bicycle", "Motor Bicycle", "Motor Bicycle", "Motor Bicycle", "Motor Bicycle"],
    "Mileage_Interval": [3000, 15000, 10000, 20000, 5000],
    "Part_Name": ["Engine Oil (1L)", "Chain Sprocket Kit", "Air Filter", "Spark Plug", "Brake Shoes (Rear)"],
    "Action": ["Change", "Replace", "Clean/Replace", "Replace", "Inspect/Replace"],
    "Urgency": ["Critical", "High", "Medium", "Medium", "High"]
}
df_bike = pd.DataFrame(bike_data)
df_bike.to_csv("data/bike_maintenance.csv", index=False)

# --- 2. THREE-WHEELER RULES (e.g., Bajaj RE 4S/2S) ---
tuk_data = {
    "Vehicle_Type": ["Three-Wheeler", "Three-Wheeler", "Three-Wheeler", "Three-Wheeler", "Three-Wheeler"],
    "Mileage_Interval": [5000, 1000, 10000, 25000, 5000],
    "Part_Name": ["Engine Oil (RE)", "Grease Nipple Service", "CV Joint (Axle)", "Canvas Hood", "Clutch Cable"],
    "Action": ["Change", "Lubricate", "Check/Replace", "Check for Leaks", "Adjust/Replace"],
    "Urgency": ["Critical", "High", "High", "Low", "Medium"]
}
df_tuk = pd.DataFrame(tuk_data)
df_tuk.to_csv("data/tuk_maintenance.csv", index=False)

# --- 3. UPDATED 2026 PRICE LIST (Adding Bike/Tuk Parts) ---
# We append these to your existing parts database
parts_data = {
    "Part_Name": [
        "Engine Oil (1L)", "Chain Sprocket Kit", "Brake Shoes (Rear)", "Spark Plug", # Bike Parts
        "Engine Oil (RE)", "CV Joint (Axle)", "Canvas Hood", "Clutch Cable", "Grease Nipple Service" # Tuk Parts
    ],
    "Base_Price_LKR": [
        2800, 8500, 1500, 850,    # Bike Prices (2026 Est)
        3200, 12500, 18000, 1200, 500 # Tuk Prices (2026 Est)
    ],
    "Import_Duty_Band": [0.15, 0.20, 0.20, 0.10, 0.15, 0.30, 0.20, 0.20, 0.0]
}
df_parts = pd.DataFrame(parts_data)
# Save as a separate file or merge with your main parts_db.csv
df_parts.to_csv("data/parts_db_special.csv", index=False)

print("✅ Bike & Tuk Datasets Created!")