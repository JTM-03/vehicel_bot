# 🚀 Quick Reference Card

## Vehicle Bot - Trip Data System

---

## 📱 Getting Started (2 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key in .env
GROQ_API_KEY=your_key_here

# 3. Run the app
streamlit run app.py

# 4. Open browser
# http://localhost:8501
```

---

## 📊 Main Features

| Feature | Location | What It Does |
|---------|----------|--------------|
| **Trip Recording** | Tab 1 | Enter 3 trips with dates |
| **Trip Table** | Tab 3 | View all trips organized |
| **Statistics** | Tab 3 | See totals and averages |
| **Charts** | Tab 3 | Road type distribution |
| **Reports** | Tab 4 | All saved diagnostics |
| **Photos** | Tab 2 | AI photo analysis |

---

## 🛣️ How to Record Trips

**For each trip, enter:**
1. **Distance** (km) - e.g., 50
2. **Road Types** - Select: City, Mountain, Carpeted, Rough
3. **Date** - When the trip happened (YYYY-MM-DD)

**Example:**
- Trip 1: 50 km | City | 2026-01-21
- Trip 2: 120 km | Carpeted, Mountain | 2026-01-20
- Trip 3: 75 km | City, Rough | 2026-01-19

---

## 📈 What Happens Next

1. ✅ Data is stored in trip table
2. ✅ AI analyzes your trip patterns
3. ✅ Generates maintenance report with costs
4. ✅ Suggests service timeline
5. ✅ Lists nearby service centers

---

## 🎯 Tab Guide

### Tab 1: 📋 Manual Diagnostic
- Enter vehicle info
- Input trip data
- Generate report

### Tab 2: 🤳 Photo Chat
- Upload image
- Ask AI questions
- Get analysis

### Tab 3: 📊 Trip Data
- See all trips
- View statistics
- Check charts
- Clear data

### Tab 4: 📜 History
- View reports
- Check timestamps
- Clear history

---

## 🔑 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Switch between form fields |
| `Enter` | Submit form (when focused on button) |
| `Ctrl+A` | Select all text |
| `Cmd+R` (Mac) | Refresh page |
| `F5` (Windows) | Refresh page |

---

## 📱 Mobile Tips

✅ Works great on phones!  
✅ Swipe to navigate tabs  
✅ Tap to select dates  
✅ Scroll for more options  

---

## ❌ Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "Missing model" | Fill vehicle model field |
| "No km entered" | Add distance to at least 1 trip |
| "API error" | Check GROQ_API_KEY in .env |
| "Date not showing" | Use YYYY-MM-DD format |
| "Data disappeared" | This is normal - data resets on refresh (optional: add MongoDB) |

---

## 📚 Documentation Files

| File | Use It For |
|------|-----------|
| README.md | Project overview |
| QUICK_START.md | Detailed user guide |
| TECHNICAL_DOCS.md | Code reference |
| ARCHITECTURE_DIAGRAMS.md | How it works |
| PROJECT_SUMMARY.md | What was completed |

---

## 🎨 UI Elements

```
🚜  App Title
📍  Location section
🔧  Maintenance section
🛣️  Trip section
📊  Data visualization
📜  History records
✅  Success message
❌  Error message
ℹ️  Info/tip box
🎈  Celebration (on success)
```

---

## 💾 Data Locations

```
Session Memory (auto-clears on refresh):
├─ trips_data      → Your recorded trips
├─ history_log     → Your reports
└─ vehicle_data    → Your vehicle info

Optional MongoDB (persistent):
├─ trips collection
├─ vehicles collection
└─ reports collection
```

---

## 🔒 Privacy

✅ No tracking  
✅ No ads  
✅ Local data only  
✅ You control everything  
✅ Clear data anytime  

---

## ⚡ Performance Tips

- Clear old data regularly (Tab 3)
- Use recent trip dates
- Keep session fresh (occasional refresh)
- Check API key is valid
- Use good internet connection

---

## 🌐 Supported Formats

**Date Format**: YYYY-MM-DD
- ✅ 2026-01-21
- ❌ 01/21/2026
- ❌ 21-01-2026

**Distance**: Whole numbers in km
- ✅ 50, 120, 75
- ❌ 50.5, 120.25

**Cost Currency**: LKR (Sri Lankan Rupees)
- Includes 18% VAT
- Includes 2.5% SSCL

---

## 🔧 Environment Variables

```bash
# Required
GROQ_API_KEY=sk_...

# Optional
MONGO_URI=mongodb+srv://...
LOG_LEVEL=INFO
```

---

## 📞 Support

**Something broken?**
→ Check [README.md](README.md) Troubleshooting section

**Want more details?**
→ Read [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)

**How does it work?**
→ See [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)

---

## 🚀 Deployment

```bash
# Local
streamlit run app.py

# Docker
docker run vehicle-bot

# Cloud
# Push to GitHub
# Deploy on Streamlit Cloud
```

---

## 📊 Sample Data

Try this to test:

**Vehicle:**
- Type: Petrol/Diesel Car
- Model: Wagon R
- Year: 2018
- Odometer: 125000 km
- City: Maharagama
- District: Colombo

**Trips:**
- Trip 1: 50km, City, Today
- Trip 2: 120km, Carpeted+Mountain, Yesterday
- Trip 3: 75km, City+Rough, 2 days ago

---

## ✅ Checklist Before Starting

- [ ] Python 3.10+ installed
- [ ] requirements.txt packages installed
- [ ] .env file with GROQ_API_KEY
- [ ] Internet connection active
- [ ] Port 8501 available

---

## 🎯 Success Indicators

✅ You'll know it's working when:
- Dashboard shows metrics
- Form accepts your input
- Report generates with costs
- Trip table displays data
- Charts show road types

---

## 📈 Monthly Workflow

```
Week 1: Record Trip 1
Week 2: Record Trip 2
Week 3: Record Trip 3
      → Generate Report
      → Review in History
      → Check Trip Data tab
      → Clear old data (optional)
```

---

## 🎉 You're All Set!

1. Run: `streamlit run app.py`
2. Enter vehicle info
3. Add your trips
4. Generate report
5. Review insights

**That's it!** 🚜✨

---

**Version**: 1.0.0  
**Last Updated**: January 21, 2026  
**Status**: Ready to Use ✅

---

*For detailed information, see the documentation files in your project folder.*
