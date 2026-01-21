# Technical Documentation - Trip Data System

## Architecture Overview

### Session State Management
```
st.session_state
├── history_log (list)
│   └── {date, model, type, content}
├── vehicle_data (dict)
│   └── {model, city, odo}
└── trips_data (list)
    └── {km, road[], date}
```

---

## Data Models

### Trip Data Structure
```python
Trip = {
    "km": int,           # Distance in kilometers (0-99999)
    "road": List[str],   # Selected road types
    "date": str          # ISO format: YYYY-MM-DD
}
```

### History Entry Structure
```python
HistoryEntry = {
    "date": str,         # Timestamp: YYYY-MM-DD HH:MM
    "model": str,        # Vehicle model name
    "type": str,         # "Diagnostic" or "Photo Analysis"
    "content": str       # Full report text (markdown)
}
```

---

## Component Breakdown

### Dashboard Metrics (Top Section)
```python
col1: Active Trips        → len(trips_data)
col2: Total Trip Distance → sum([t['km'] for t in trips_data])
col3: Latest Trip Date    → max([t['date'] for t in trips_data])
```

### Trip Entry Layout
```
Main Form (3 columns)
├── Trip 1 (Column 1)
│   ├── Distance input
│   ├── Road type multiselect
│   └── Date picker (default: today)
├── Trip 2 (Column 2)
│   ├── Distance input
│   ├── Road type multiselect
│   └── Date picker (default: yesterday)
└── Trip 3 (Column 3)
    ├── Distance input
    ├── Road type multiselect
    └── Date picker (default: 2 days ago)
```

### Trip Data Tab Components
```python
Tab 3: Trip Data Visualization
├── Data Table
│   └── DataFrame(trips_data) - sortable
├── Metrics Cards (3 columns)
│   ├── Total Distance
│   ├── Average Distance
│   └── Trip Count
├── Road Type Chart
│   └── pd.Series.value_counts() → bar_chart
└── Clear Data Button
    └── Reset trips_data
```

### History Tab Components
```python
Tab 4: History Records
├── Record Counter
│   └── len(history_log)
├── Expandable Records
│   └── For each entry: expander(date - model - type)
└── Clear History Button
    └── Reset history_log
```

---

## Data Flow

### Adding a Trip
```
User Input
    ↓
Form Validation (model ✓, km > 0 ✓)
    ↓
Create Trip Dict: {km, road, date}
    ↓
Append to trips_data
    ↓
Generate Report
    ↓
Create History Entry
    ↓
Append to history_log
    ↓
Display Success + Balloons
```

### Viewing Trip Data
```
Tab 3: Trip Data
    ↓
Check trips_data length
    ↓
If empty: Show info message
    ↓
If populated:
  ├─ Create DataFrame
  ├─ Display table
  ├─ Calculate stats
  ├─ Generate road type chart
  └─ Show clear button
```

---

## Integration with AI Analysis

### Report Generation (logic.py)
```python
def get_advanced_report(v_type, model, m_year, odo, 
                       district, city, tyre_odo, align_odo, 
                       service_odo, trips)
```

**Input Processing:**
1. Extract trip dates, km, and road types
2. Format summary string:
   ```
   Trip 1 (2026-01-21): 50km on City roads
   Trip 2 (2026-01-20): 120km on Carpeted, Mountain roads
   Trip 3 (2026-01-19): 75km on City, Rough roads
   ```
3. Pass to LLM with enhanced prompt

**Prompt Enhancement:**
- Includes `RECENT TRIP DATA WITH DATES` section
- Requests analysis of trip patterns
- Asks for date-based maintenance timeline
- Considers frequency and timing

---

## Error Handling

### Validation Rules
```python
if submit:
    if not model:
        st.error("❌ Please enter vehicle model")
    elif not any([t["km"] > 0 for t in trips]):
        st.error("❌ Please enter at least one trip distance")
    else:
        # Process successfully
```

### Data Safety
- **Persistent Storage**: Uses session state (not database by default)
- **Clear Buttons**: Allow users to reset data anytime
- **No Auto-delete**: Data persists until explicitly cleared
- **Error Messages**: Clear feedback on what went wrong

---

## Performance Considerations

### Data Size Limits
- **trips_data**: No hard limit, but UI optimized for 3-100 trips
- **history_log**: No hard limit, expandable design for scalability
- **Each trip**: ~200 bytes
- **Each history entry**: ~2-50KB (variable with report size)

### Optimization Strategies
```python
# Efficient date extraction
latest_date = max([t.get("date", "") for t in trips_data])

# Efficient road type counting
all_roads = []
for roads in trip_df['road']:
    all_roads.extend(roads if isinstance(roads, list) else [])
road_counts = pd.Series(all_roads).value_counts()

# DataFrame operations for display
trip_df_display = trip_df.copy()
trip_df_display['road'] = trip_df_display['road'].apply(
    lambda x: ', '.join(x) if isinstance(x, list) else x
)
```

---

## Streamlit-Specific Features Used

### Form Handling
```python
with st.form("main_form"):
    # All inputs here are grouped
    submit = st.form_submit_button("Generate Report")
if submit:
    # Process only when button clicked
```

### Session State
```python
if "trips_data" not in st.session_state:
    st.session_state.trips_data = []
# Persists across reruns within same session
```

### Layout Components
```python
st.columns(3)           # Responsive 3-column layout
st.tabs([...])          # Tab navigation
st.expander(...)        # Collapsible sections
st.metric(...)          # KPI cards
st.dataframe(...)       # Sortable tables
st.bar_chart(...)       # Simple charting
st.form_submit_button() # Grouped submissions
```

### User Feedback
```python
st.success()    # Green success message
st.error()      # Red error message
st.info()       # Blue info message
st.balloons()   # Celebration animation
st.rerun()      # Force page refresh
```

---

## Future Enhancement Opportunities

### Data Persistence
```python
# Option 1: MongoDB Integration
def save_trips(user_id, trips_data):
    db = get_db_client()
    db.trips.insert_many(trips_data)

# Option 2: CSV Export
def export_trips(trips_data):
    df = pd.DataFrame(trips_data)
    return df.to_csv()
```

### Advanced Analytics
```python
# Trip frequency analysis
trip_dates = [t['date'] for t in trips_data]
date_diffs = [trip_dates[i-1] - trip_dates[i] for i in range(1, len(trip_dates))]
avg_frequency = np.mean([d.days for d in date_diffs])

# Mileage trends
weekly_km = sum([t['km'] for t in trips_data if week_check(t['date'])])
monthly_km = sum([t['km'] for t in trips_data if month_check(t['date'])])

# Road type preferences
road_distribution = Counter([road for t in trips_data for road in t['road']])
most_common_road = road_distribution.most_common(1)
```

### Predictive Features
```python
# Maintenance due calculation
def maintenance_due_date(service_odo, current_odo, avg_monthly_km):
    km_until_service = 5000 - (current_odo - service_odo)
    months_until_service = km_until_service / avg_monthly_km
    return datetime.now() + timedelta(days=months_until_service * 30)

# Alert system
if days_until_service < 30:
    st.warning(f"⚠️ Service due in {days_until_service} days!")
```

---

## Testing Checklist

- [ ] Form submission with valid data
- [ ] Form validation (missing model)
- [ ] Form validation (zero km trips)
- [ ] Trip data storage
- [ ] Trip data display in Tab 3
- [ ] Statistics calculation
- [ ] Road type chart generation
- [ ] Clear trip data functionality
- [ ] History record creation
- [ ] History display with expandable items
- [ ] Clear history functionality
- [ ] Date picker default values
- [ ] Dashboard metrics update
- [ ] Photo upload and analysis
- [ ] Cross-session persistence
- [ ] Mobile responsive layout

---

**Last Updated:** January 21, 2026  
**Version:** 1.0  
**Status:** Production Ready ✅
