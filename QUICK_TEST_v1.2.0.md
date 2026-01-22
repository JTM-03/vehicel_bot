# Quick Test Guide - v1.2.0 Features

## 1. Test Parts Mileage Data in Risk Analysis (5 min)

### Steps:
1. Run app: `streamlit run app.py`
2. Fill in vehicle details:
   - Type: "Car"
   - Model: "Honda Civic"
   - Year: 2020
   - Current odometer: 50,000 km
   - Last service: 40,000 km
   - Last alignment: 45,000 km

3. Add at least one trip with distance

4. **Select parts replaced:**
   - Check "Brake Pads"
   - Check "Engine Oil"

5. **Enter mileage when replaced:**
   - Brake Pads: 45,000 km
   - Engine Oil: 48,000 km

6. Click "Generate Predictive Report"

### Verify:
- Look for text mentioning "km ago" for parts
- Check risk analysis mentions "recently replaced"
- Risk should be reduced due to recent replacements
- Report should show impact on accident risk percentage

---

## 2. Test Clear Chat Button (3 min)

### Steps:
1. Go to "💬 AI Mechanic Chat" tab
2. Type a message: "How often should I change my oil?"
3. Click "💬 Send Message"
4. Wait for response
5. Type another message: "What about brake fluid?"
6. Click "💬 Send Message"
7. **Now click "🔄 Clear Chat"**

### Verify:
- Chat history disappears immediately
- No error messages
- Page doesn't freeze or reload unnecessarily
- You can send new messages after clearing

---

## 3. Test Form Refresh with Trips & Parts (5 min)

### Steps:
1. Go to "📋 Diagnostic & Report" tab
2. Fill in vehicle data:
   - Model: "Toyota Fortuner"
   - Type: "Car"
   - City: "Colombo"
   - Odometer: 75,000 km

3. Add three trips:
   - Trip 1: 50 km, City roads
   - Trip 2: 30 km, Mountain roads
   - Trip 3: 20 km, Rough roads

4. Select parts replaced:
   - Tyres
   - Battery
   - Air Filter

5. **Click "🔄 Refresh Form"**

### Verify:
- ✅ Model field is cleared
- ✅ Odometer field is cleared
- ✅ All three trip fields are cleared
- ✅ Parts selection is cleared
- ✅ You can fill new data without old values showing

---

## 4. Test Gemini Photo Analysis (5 min)

### Steps:
1. Go to "💬 AI Mechanic Chat" tab
2. Click "Upload vehicle image"
3. Select a clear photo of any vehicle part (tire, engine, brake, etc.)
4. Type question: "What's the condition of this part and what maintenance does it need?"
5. Click "💬 Send Message"
6. Wait for Gemini analysis

### Verify:
- Image loads and shows preview
- No error about unsupported format
- Response includes:
  - What component was identified
  - Condition assessment (Good/Fair/Poor/etc.)
  - Issues found
  - Maintenance recommendations
  - Estimated cost in LKR
  - Urgency level
  - Safety impact
  - Tips for Sri Lanka climate

### Try with different photos:
- Tire tread wear
- Brake pads
- Battery terminals
- Engine oil level
- Windshield wipers

---

## Expected Outputs

### Parts Mileage Report Example:
```
RECENT PARTS REPLACED:
- Brake Pads (replaced at 45000km, 5000km ago)
- Engine Oil (replaced at 48000km, 2000km ago)

Risk Analysis includes:
"Recently replaced parts will reduce accident risk by approximately 5% per part"
```

### Clear Chat:
```
Before: Message 1, Message 2, Message 3
Click Clear Chat
After: Empty chat history
```

### Form Refresh:
```
Before:
- Model: "Honda Civic"
- Odometer: 50000
- Trips: [50km, 30km, 20km]
- Parts: [Brake Pads, Oil, Filter]

Click Refresh Form

After:
- Model: ""
- Odometer: 0
- Trips: [empty, empty, empty]
- Parts: []
```

### Gemini Photo Analysis:
```
**What I See:**
Brake pads on Honda Civic, rear left

**Condition Assessment:**
Fair - Shows moderate wear

**Issues Identified:**
- Wear depth: ~50% remaining
- Some glazing on surface
- Slight unevenness

**Recommended Maintenance:**
Replace within next 2,000 km for safety

**Estimated Cost (LKR):**
2,500 + VAT 18% (450) + SSCL 2.5% (72) = ~3,000 LKR

**Urgency Level:**
High Priority

**Safety Impact:**
Reduced braking efficiency in wet conditions, increases accident risk by ~15%

**Tips & Best Practices:**
Use quality brake pads suited for Sri Lankan traffic conditions
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Parts mileage not showing | Make sure you selected parts AND entered mileage before submitting |
| Clear Chat button not working | Hard refresh (Ctrl+Shift+R) and restart Streamlit |
| Form not refreshing completely | Click refresh again or reload page |
| Photo shows "unsupported format" | Try JPG or PNG format, ensure file is valid image |
| Gemini error "API key not found" | Check GOOGLE_API_KEY is in .env file |
| Photo analysis shows generic response | Upload clearer, well-lit image of specific part |

---

## Quick Commands

```bash
# Run the app
cd d:\Vehicle_Bot
streamlit run app.py

# Install updated dependencies
pip install -r requirements.txt

# Check environment variables
# Make sure these are in .env:
# - GOOGLE_API_KEY (for Gemini)
# - GROQ_API_KEY (for Groq)

# Restart Python environment
deactivate
.venv\Scripts\activate
pip install google-generativeai
streamlit run app.py
```

---

## Success Criteria

Your implementation is working if:

✅ Parts mileage appears in the report with "km ago" notation
✅ Risk analysis mentions reduced risk from recent parts
✅ Clear Chat button removes chat history instantly
✅ Form refresh clears ALL fields (vehicle, trips, parts)
✅ Photo analysis includes detailed Gemini response
✅ Photo analysis mentions cost, condition, urgency
✅ No error messages for valid inputs
✅ System handles gracefully when API unavailable

---

## Time Estimate: 20-30 minutes total testing

- Parts Mileage: 5 min
- Clear Chat: 3 min
- Form Refresh: 5 min
- Photo Analysis: 5-10 min (with different photos)
- Troubleshooting: As needed

---

Ready to test? Good luck! 🚗
