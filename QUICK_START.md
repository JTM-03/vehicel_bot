# 🚜 Sri Lanka Pro-Vehicle Engine - Quick Start Guide

## What's New?

### ✨ Three Trip Data Collection with Dates
Your vehicle maintenance bot now tracks **3 recent trips** with:
- 📍 Trip distance (km)
- 🗺️ Road types (City, Mountain, Carpeted, Rough)
- 📅 **Trip dates** - When each trip was made

This helps the AI provide more accurate maintenance predictions!

---

## 📱 How to Use the New Features

### Step 1: Input Vehicle Information
1. Fill in your vehicle details:
   - Vehicle type (Car, Motorbike, etc.)
   - Vehicle model
   - District & nearest city
   - Current odometer reading
   - Year of manufacture

### Step 2: Maintenance History
Enter your recent maintenance data:
- Last service odometer reading
- Last alignment odometer reading

### Step 3: Record 3 Trips *(NEW!)*
For each of your last 3 trips, enter:

**Trip 1 (Most Recent)**
- Distance traveled (km)
- Road types encountered
- Date of trip

**Trip 2**
- Distance traveled (km)
- Road types encountered
- Date of trip

**Trip 3**
- Distance traveled (km)
- Road types encountered
- Date of trip

> 💡 **Tip**: These dates help the AI understand your driving patterns and recommend maintenance timing!

### Step 4: Generate Report
Click "🔍 Generate Predictive Report" to get:
- Road & environment warnings specific to your area
- 2026 maintenance costs in LKR
- Recommended service centers near you
- Maintenance timeline based on your trip dates

---

## 📊 View Your Trip Data

### Trip Data Tab
Shows all your recorded trips in a table with:
- Distance for each trip
- Road types used
- Trip dates
- **Statistics**: Total km, average distance, trip count
- **Chart**: Visual breakdown of road type usage

### History Tab
All your diagnostic reports saved with:
- Timestamp
- Vehicle model
- Report type
- Full report details

---

## 🎯 Key Benefits

### For Vehicle Owners
✅ Track actual driving patterns  
✅ Get accurate maintenance recommendations  
✅ See costs in 2026 LKR with taxes  
✅ Find nearby service centers  

### For Mechanics
✅ Real trip data for diagnostics  
✅ Date-based maintenance timeline  
✅ Area-specific recommendations  

---

## 📌 Tips & Tricks

### Road Types to Track
- **Carpeted** - Well-maintained highways
- **City** - Urban roads and traffic
- **Mountain** - Hilly/mountainous terrain
- **Rough** - Poor quality, unpaved roads

### Best Practices
1. **Be accurate** with trip distances
2. **Select all applicable road types** for each trip
3. **Update dates** correctly for timeline accuracy
4. **Review stored trips** in the Trip Data tab
5. **Save reports** you find useful

### Data Management
- View all stored trips in **Trip Data tab**
- Clear trip data with "🗑️ Clear All Trip Data" button
- Clear reports with "🗑️ Clear All History" button
- All data persists during your session

---

## 🔄 Workflow Example

**Friday (2026-01-17)**: Drive 50km on City roads
→ Enter: Trip 1: 50km, City, 2026-01-17

**Sunday (2026-01-19)**: Drive 120km (40km Carpeted + 80km Mountain)
→ Enter: Trip 2: 120km, Carpeted + Mountain, 2026-01-19

**Tuesday (2026-01-21)**: Drive 75km (50km City + 25km Rough)
→ Enter: Trip 3: 75km, City + Rough, 2026-01-21

**Click Generate Report** → Get predictions based on these exact patterns!

---

## ❓ Frequently Asked Questions

**Q: Do I need all 3 trips filled?**  
A: No, but more trip data = better predictions!

**Q: How are dates used?**  
A: Helps determine maintenance urgency and schedule

**Q: Can I update dates?**  
A: Yes, dates default to recent days but you can change them

**Q: Where is my data saved?**  
A: Data stays in your session. Use History tab to review past reports

**Q: How often should I update trips?**  
A: Every 3-4 weeks for accurate pattern tracking

---

## 🚀 Ready to Start?

1. Open the app: `streamlit run app.py`
2. Go to **Manual Diagnostic** tab
3. Enter your vehicle info
4. Add your 3 recent trips with dates
5. Click **Generate Predictive Report**
6. View your Trip Data & History!

---

**Version**: 2026.01  
**Last Updated**: January 21, 2026

Happy tracking! 🚜✨
