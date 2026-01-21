# 🔐 User Management & Data Persistence Guide

## Vehicle Bot v1.1.0 - Multi-User Support

**Release Date**: January 21, 2026  
**Feature**: User Identification & Database Storage

---

## 🎯 What's New

### User Identification System
Each user is identified by a unique combination of:
- **Vehicle Model** (e.g., "Wagon R")
- **City/Living Area** (e.g., "Maharagama")

This creates a **unique User ID** that persists across sessions.

### Key Features Added

✅ **Automatic User Identification**
- Users identified by vehicle model + city
- Unique User ID generated and displayed
- Persistent across browser sessions

✅ **Data Persistence**
- All user data saved to MongoDB
- Auto-loaded on next visit
- No data loss between sessions

✅ **Multi-User Support**
- Switch between different users
- View all registered users
- Load any user's data instantly

✅ **Change Tracking**
- Every modification logged
- Service odometer changes tracked
- Trip additions recorded
- Reports logged with timestamps

✅ **Data Import/Export**
- Changes log can be exported
- CSV format for analysis
- Complete audit trail

---

## 👤 User Profile Section

### Location: Top of Application

```
┌─────────────────────────────────────────────────────────┐
│ 👤 User Profile & Identification                        │
├──────────────┬──────────────┬──────────────┬────────────┤
│ 🔑 User ID   │ 🚗 Vehicle   │ 📍 Location  │ ✅ Status  │
│ abc123...    │ Car: Wagon R │ Colombo,     │ Data       │
│              │              │ Maharagama   │ Loaded     │
└──────────────┴──────────────┴──────────────┴────────────┘
```

The profile section shows:
- **User ID**: Unique identifier for this user
- **Vehicle**: Type and model
- **Location**: District and city
- **Status**: New user or Data Loaded

---

## 🔄 User Management Controls

### Load Existing User
```
📂 Load Existing User (Dropdown)
  ↓
  🆕 New User
  Wagon R - Maharagama
  Pulsar 150 - Kandy
  Three-Wheeler - Galle

[⬇️ Load Selected User]
```

### View All Users
```
[📊 View All Users]
  ↓
  Displays table of all registered users:
  - Model | City | District | Created Date
```

### Start New Session
```
[🗑️ Start New Session]
  ↓
  Clears current session
  Ready for new user
```

---

## 💾 Saving User Data

### First Time User
1. Enter all vehicle information
2. Fill in maintenance history
3. **Click "💾 Save User Profile to Database"**
4. User ID is generated and saved
5. Data persists to MongoDB

### Auto-Save on Report Generation
When you generate a report, data is automatically saved to database if user is loaded.

### Manual Updates
Users can update:
- Service odometer
- Alignment odometer
- Trip data

All changes are logged.

---

## 📊 How User Identification Works

### User ID Generation

```python
User ID = MD5_Hash(Vehicle_Model + City)[:12]

Example:
  Vehicle: "Wagon R"
  City: "Maharagama"
  Result: User ID = "abc123def456"
```

### Why This Approach?

✅ **Unique**: Model + City combination is unique per user  
✅ **Consistent**: Same model + city always generates same ID  
✅ **Anonymous**: Doesn't reveal personal information  
✅ **Simple**: Users just enter model and city  
✅ **Portable**: Works across devices  

---

## 🔁 User Workflow Examples

### First Time User (New Vehicle Owner)

```
Step 1: Open app
Step 2: User Profile shows "🆕 No user loaded"
Step 3: Enter vehicle info (Model: Wagon R, City: Maharagama)
Step 4: Enter maintenance & trip data
Step 5: Click "💾 Save User Profile to Database"
Step 6: User ID generated: abc123def456
Step 7: Message: "✅ Profile saved! User ID: abc123def456"
Step 8: Data stored in MongoDB
```

### Returning User (Same Device)

```
Step 1: Open app
Step 2: User Management shows "📂 Load Existing User"
Step 3: Dropdown shows: "Wagon R - Maharagama"
Step 4: Click [⬇️ Load Selected User]
Step 5: Form auto-fills with:
       - Vehicle Model: Wagon R
       - City: Maharagama
       - District: Colombo
       - Service Odometer: 100000
       - Alignment Odometer: 80000
       - Previous Trips: Loaded
Step 6: Message: "✅ Data Loaded from Database"
Step 7: Can now update or generate new report
```

### Returning User (Different Device)

```
Step 1: Open app on new device
Step 2: No users shown in dropdown (fresh device)
Step 3: Enter vehicle info (Model: Wagon R, City: Maharagama)
Step 4: Click "💾 Save User Profile to Database"
Step 5: System recognizes same model + city = same user
Step 6: Loads existing user data from MongoDB
Step 7: All previous data appears
```

### Switching Between Users

```
Step 1: Currently viewing User A (Wagon R, Maharagama)
Step 2: Click [🗑️ Start New Session]
Step 3: Message: "🆕 Session cleared"
Step 4: Enter different vehicle info (Model: Pulsar 150, City: Kandy)
Step 5: Click "💾 Save User Profile to Database"
Step 6: New user created: User B
Step 7: Can switch back anytime using dropdown
```

---

## 📝 Changes & Modifications Log

### What Gets Tracked?

**✅ Service Odometer Updates**
```
2026-01-21 14:30 | Last Service Updated | 100000 → 105000 km
```

**✅ Alignment Odometer Updates**
```
2026-01-21 15:00 | Last Alignment Updated | 80000 → 85000 km
```

**✅ Trip Additions**
```
2026-01-21 16:00 | Trip Added | 50 km | City roads | 2026-01-21
```

**✅ Report Generations**
```
2026-01-21 16:30 | Report Generated | Diagnostic type
```

### Changes Log Tab

Location: **Tab 5 - 📝 Changes Log**

Features:
- Shows all modifications to user data
- Sorted newest first
- Shows old value → new value
- Includes timestamp
- **Export as CSV** for record keeping

---

## 🗄️ Database Structure

### User Document Schema

```json
{
  "user_id": "abc123def456",
  "model": "Wagon R",
  "city": "Maharagama",
  "district": "Colombo",
  "created_date": "2026-01-21T14:00:00",
  "last_updated": "2026-01-21T16:30:00",
  
  "vehicle_data": {
    "v_type": "Petrol/Diesel Car",
    "model": "Wagon R",
    "city": "Maharagama",
    "district": "Colombo",
    "odo": 125000,
    "m_year": 2018,
    "s_odo": 120000,
    "a_odo": 110000
  },
  
  "trips_data": [
    {
      "km": 50,
      "road": ["City"],
      "date": "2026-01-21"
    },
    ...
  ],
  
  "history_log": [
    {
      "date": "2026-01-21 14:30",
      "model": "Wagon R",
      "type": "Diagnostic",
      "content": "Report text..."
    },
    ...
  ],
  
  "changes_log": [
    {
      "timestamp": "2026-01-21T14:30:00",
      "field": "last_service_odometer",
      "old_value": 115000,
      "new_value": 120000,
      "changed_by": "user_update"
    },
    ...
  ]
}
```

---

## 🔒 Data Security & Privacy

### How Data is Protected

✅ **User ID is Anonymous**
- Based on vehicle model + city, not personal info
- No names, phone numbers, or emails stored

✅ **Database Connection Optional**
- App works without MongoDB
- Can use session-only mode
- Data stays on device if no database configured

✅ **Change Tracking**
- You can see every modification
- Audit trail for all changes
- Export for backup

✅ **User Control**
- Start new session anytime
- Clear data with one click
- Export changes as needed

---

## ⚙️ Configuration

### Enable Database Persistence

1. **Set MongoDB URI in .env**
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   ```

2. **Database Auto-Creates**
   - `vehicle_bot_db` database
   - `users` collection
   - Automatically indexes on `user_id`

3. **Optional Features**
   - Works without MongoDB
   - Falls back to session-only mode
   - No errors if database unavailable

---

## 💡 Usage Tips

### Best Practices

**✅ Save Profile First**
- Click "💾 Save User Profile" after entering vehicle info
- Ensures all data is safely stored

**✅ Check User Status**
- Look at top right corner for data status
- "✅ Data Loaded" vs "🆕 New User Session"

**✅ Use Changes Log**
- Review what changed over time
- Export CSV for record keeping
- Track service patterns

**✅ Load Before Editing**
- Load user first
- Form auto-fills with existing data
- Then make updates

### Common Questions

**Q: What if I forget my user info?**  
A: Look in "View All Users" - shows all registered users

**Q: Can I use same app for 2 vehicles?**  
A: Yes! Use "Start New Session" and add different vehicle model/city

**Q: Is my data lost if I close browser?**  
A: No! It's saved in MongoDB. Just load user again when you return.

**Q: How do I update service odometer?**  
A: Load user, change the service odometer value, click "Generate Report" (auto-saves)

**Q: Can I export my data?**  
A: Yes! Changes log can be exported as CSV from Tab 5

---

## 🔄 Data Synchronization

### Auto-Save Features

**Automatic Saves Occur When:**
- ✅ Profile saved (explicit click)
- ✅ Report generated (auto-updates trips & history)
- ✅ Service odometer changed
- ✅ Alignment odometer changed
- ✅ Trip data added

**Manual Save:**
- Click "💾 Save User Profile to Database" anytime

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| User not saving | Check MongoDB connection in .env |
| Data not loading | Make sure model + city exactly match previous entry |
| Multiple users same model | Add different city to distinguish |
| Can't find user | Check "View All Users" to see registered users |
| Lost data | Check Changes Log - see what was modified |

---

## 📈 Data Management

### What Data is Stored Per User?

```
✅ Vehicle Information
   - Type, model, year, odometer
   
✅ Maintenance History
   - Service odometer, alignment odometer
   
✅ Trip Data
   - All recorded trips with dates
   - Road types and distances
   
✅ Diagnostic Reports
   - All generated reports with timestamps
   
✅ Change History
   - Every modification logged
   - Before/after values
   - Timestamps
```

### Storage Capacity

- **No limits** on number of trips
- **No limits** on number of reports
- **No limits** on change log entries
- Designed to scale indefinitely

---

## 🚀 Future Enhancements

### Planned Features

📅 **Maintenance Reminders**
- Notify when service due
- Based on trip patterns

📊 **Analytics Dashboard**
- Trip trends over time
- Maintenance spending analysis
- Road type preferences

👥 **User Sharing**
- Share profiles with mechanics
- Allow mechanic notes

📱 **Mobile App**
- Native iOS/Android app
- Same user profiles

☁️ **Cloud Sync**
- Auto-sync across devices
- Cloud backup

---

## 📚 Integration with Other Features

### Manual Diagnostic Tab
- Form pre-fills with loaded user data
- Updates save to database
- Changes tracked automatically

### Trip Data Tab
- Shows all user's trips
- Can clear from database
- Statistics updated from stored data

### History Tab
- Shows all user's reports
- Each report saved to database
- Clear deletes from database too

### Changes Log Tab (NEW!)
- Shows timeline of all modifications
- Export capability
- Complete audit trail

---

## 🔑 Key Features Summary

| Feature | Benefit |
|---------|---------|
| User ID | Persistent identification across sessions |
| Auto-Load | Form fields pre-fill automatically |
| Database Persistence | Data survives browser close |
| Change Tracking | Complete audit trail |
| Multi-User Support | Use for multiple vehicles |
| Export Capability | Download changes as CSV |
| User Switching | Easy switching between users |
| Anonymous | No personal data stored |

---

## ✅ Implementation Checklist

For developers implementing this feature:

- ✅ User ID generation based on model + city
- ✅ MongoDB save/load functions
- ✅ Form pre-population logic
- ✅ Change tracking on updates
- ✅ User management UI
- ✅ Multi-user dropdown
- ✅ Changes log display
- ✅ CSV export functionality
- ✅ Session state management
- ✅ Database connection fallback

---

## 📞 Support Resources

- **README.md** - General overview
- **QUICK_START.md** - Getting started guide
- **TECHNICAL_DOCS.md** - Developer reference
- **ARCHITECTURE_DIAGRAMS.md** - System design
- **This Document** - User management specifics

---

**Version**: 1.1.0  
**Release Date**: January 21, 2026  
**Status**: ✅ Production Ready

For questions or feedback, refer to the complete documentation set.
