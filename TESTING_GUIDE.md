# Quick Testing Guide

## How to Test the Dataset Integration

### Test 1: Run the Streamlit App
```bash
cd d:\Vehicle_Bot
streamlit run app.py
```

Then in the UI:
1. Fill in vehicle details (e.g., 2015 Honda Civic)
2. Enter current odometer: 50000 km
3. Enter last service: 40000 km
4. Add a few trips with road conditions
5. Click "Generate Report"

**Expected Result:**
- Maintenance recommendations come from dataset (not AI generated)
- OBD codes shown with descriptions from CSV
- Weather data fetched from wttr.in
- Shops from local Sri Lankan database

---

### Test 2: Test Bike Maintenance
**Input:**
- Vehicle Type: Motorbike
- Model: Honda CD70
- Year: 2020
- Odometer: 15000 km
- Last Service: 10000 km

**Expected Output:**
- Engine Oil (1L): CRITICAL - 2800 LKR
- Spark Plug: HIGH - 850 LKR
- (More parts as interval is exceeded)

---

### Test 3: Test Three-Wheeler Maintenance
**Input:**
- Vehicle Type: Three-Wheeler (Tuk)
- Model: Bajaj RE
- Year: 2018
- Odometer: 20000 km
- Last Service: 15000 km

**Expected Output:**
- Engine Oil (RE): CRITICAL - 3200 LKR
- Grease Nipple Service: CRITICAL - 500 LKR
- CV Joint: HIGH - 12500 LKR

---

### Test 4: OBD Code Lookup
If the app has an OBD code lookup feature:

**Test Codes:**
- `P0100` → Mass or Volume Air Flow Circuit Malfunction
- `P0101` → Mass or Volume Air Flow Circuit Range/Performance Problem
- `P0200` → Engine Oil Temperature Sensor Intermittent

---

## What's Different From Before

### Before (Old System)
```
User: "What maintenance does my bike need?"
AI: "Based on general bike maintenance patterns, you probably need..."
(Generated recommendations - could vary each time)
```

### After (New System)
```
User: "What maintenance does my bike need?"
Dataset: "Bike with 15000 km since service (last at 10000 km) needs:"
- Engine Oil (every 3000 km) ✓ Due
- Spark Plug (every 5000 km) ✓ Due
- Air Filter (every 10000 km) - Not due yet
(Consistent, database-backed recommendations)
```

---

## Troubleshooting

### If you see: "Could not load maintenance schedule"
**Solution:** Make sure `maintain_schdule.csv` is in the root directory

### If OBD codes show as empty
**Solution:** Verify `obd-trouble-codes.csv` exists with format: Code,Description

### If shops show "Unknown"
**Solution:** This is normal - dataset has data for major cities. For other locations, generic shops are shown.

---

## Performance Notes

- **First run**: Loads CSV files (takes 1-2 seconds)
- **Subsequent runs**: Uses Streamlit cache (instant)
- **Weather API**: Called once per session (fast)
- **No API calls for maintenance**: Pure dataset lookup

---

## Key Files

1. **datasets.py** - Contains DatasetHandler class
2. **logic.py** - Calls `dataset_handler.get_maintenance_recommendations()`
3. **app.py** - Displays results (no changes needed)
4. **maintain_schdule.csv** - Reference data for maintenance
5. **obd-trouble-codes.csv** - 3072 OBD code mappings

---

## Success Indicators

Your integration is working if:

✅ App loads without errors
✅ Bike maintenance shows specific parts (Oil, Spark Plug, etc.)
✅ Three-wheeler maintenance shows different parts (Grease, CV Joint, etc.)
✅ Car maintenance shows generic recommendations
✅ OBD codes return descriptions (not "Unknown")
✅ Shops show real Sri Lankan locations
✅ Weather data displays for the city
✅ Reports export to PDF/CSV successfully

---

## Support

If something isn't working:

1. Check that all CSV files are in `d:\Vehicle_Bot\` directory
2. Verify file names match exactly:
   - `maintain_schdule.csv` (note: not "schedule")
   - `obd-trouble-codes.csv`
3. Make sure `datasets.py` is imported correctly in `logic.py`
4. Check for Python syntax errors: `python -m py_compile datasets.py`

---

Done! The system is ready to use. 🚗🏍️🛺
