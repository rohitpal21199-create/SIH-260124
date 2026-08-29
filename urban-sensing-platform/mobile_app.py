"""
Urban Sensing Platform - Mobile App (Streamlit)
"""

import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Urban Sensing - NAPP",
    page_icon="🚍",
    layout="wide"
)

# ============================================
# API CONFIG
# ============================================
API_URL = "http://localhost:8000"

# ============================================
# SESSION STATE
# ============================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# ============================================
# HELPER FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_events():
    try:
        response = requests.get(f"{API_URL}/api/events")
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=10)
def fetch_stats():
    try:
        response = requests.get(f"{API_URL}/api/stats")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

@st.cache_data(ttl=10)
def fetch_alerts():
    try:
        response = requests.get(f"{API_URL}/api/alerts")
        return response.json() if response.status_code == 200 else []
    except:
        return []

# ============================================
# LOGIN PAGE
# ============================================
if not st.session_state.logged_in:
    st.title("🚍 Urban Sensing Platform")
    st.subheader("Login")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 Citizen Login", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_type = "citizen"
            st.rerun()
    
    with col2:
        if st.button("🏛️ Authority Login", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_type = "authority"
            st.rerun()
    
    st.info("👤 Demo Login: Click Citizen or Authority button")
    st.stop()

# ============================================
# MAIN APP
# ============================================

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.write("🚍")
with col2:
    st.title("Urban Sensing Platform")
with col3:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.rerun()

st.markdown(f"👤 Logged in as: **{st.session_state.user_type.upper()}**")
st.markdown("---")

# ============================================
# SIDEBAR NAVIGATION
# ============================================
st.sidebar.title("📊 Navigation")

if st.session_state.user_type == "citizen":
    page = st.sidebar.radio(
        "Go to:",
        ["🏠 Dashboard", "📸 Report Pothole", "🗺️ Nearby Issues", "🚨 Alerts"]
    )
else:
    page = st.sidebar.radio(
        "Go to:",
        ["🏠 Dashboard", "🗺️ GIS Map", "🔥 Heatmap", "🚨 Alerts", "📈 Analytics", "📄 Reports"]
    )

# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "🏠 Dashboard":
    st.subheader("📊 Dashboard")
    
    stats = fetch_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", stats.get('total_events', 0))
    col2.metric("Objects Detected", stats.get('total_objects', 0))
    col3.metric("Road Defects", stats.get('total_defects', 0))
    col4.metric("Active Buses", stats.get('unique_buses', 0))
    
    st.markdown("---")
    
    st.subheader("📋 Recent Events")
    events = fetch_events()
    if events:
        df = pd.DataFrame(events[-10:])
        st.dataframe(df[['timestamp', 'bus_id', 'objects', 'road_defects', 'location']])
    else:
        st.info("No events found. Add events via Swagger UI!")

# ============================================
# PAGE: MAP VIEW
# ============================================
elif page == "🗺️ GIS Map" or page == "🗺️ Nearby Issues":
    st.subheader("🗺️ Map View")
    
    events = fetch_events()
    
    m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)
    
    for event in events[-50:]:
        try:
            lat, lon = map(float, event.get('location', '0,0').split(','))
            
            if event.get('road_defects'):
                color = 'red'
                icon = 'exclamation-triangle'
                popup = f"🚨 {event['road_defects'][0]}<br>📍 {event.get('location')}"
            elif event.get('objects'):
                color = 'blue'
                icon = 'bus'
                popup = f"🚌 {event['objects'][0]}<br>📍 {event.get('location')}"
            else:
                color = 'green'
                icon = 'info-circle'
                popup = f"ℹ️ Event<br>📍 {event.get('location')}"
            
            folium.Marker(
                [lat, lon],
                popup=popup,
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)
        except:
            continue
    
    st_folium(m, width=900, height=500)

# ============================================
# PAGE: HEATMAP
# ============================================
elif page == "🔥 Heatmap":
    st.subheader("🔥 Congestion & Defect Heatmap")
    
    events = fetch_events()
    
    defects = []
    for event in events:
        if event.get('road_defects'):
            try:
                lat, lon = map(float, event.get('location', '0,0').split(','))
                defects.append([lat, lon])
            except:
                continue
    
    if defects:
        m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)
        from folium.plugins import HeatMap
        HeatMap(defects, radius=15).add_to(m)
        st_folium(m, width=900, height=500)
    else:
        st.info("No defects found. Add some events first!")

# ============================================
# PAGE: REPORT POTHOLES
# ============================================
elif page == "📸 Report Pothole":
    st.subheader("📸 Report a Pothole")
    
    with st.form("report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.number_input("📍 Latitude", value=19.0760, format="%.6f")
            longitude = st.number_input("📍 Longitude", value=72.8777, format="%.6f")
        
        with col2:
            severity = st.selectbox("⚠️ Severity", ["Mild", "Moderate", "Severe"])
            description = st.text_area("📝 Description", placeholder="Describe the issue...")
        
        image_file = st.file_uploader("📷 Upload Photo", type=['jpg', 'png', 'jpeg'])
        
        submitted = st.form_submit_button("📤 Submit Report")
        
        if submitted:
            data = {
                "timestamp": datetime.now().isoformat(),
                "bus_id": "CITIZEN-001",
                "event_type": "manual_report",
                "latitude": latitude,
                "longitude": longitude,
                "objects": [],
                "road_defects": [severity.lower()],
                "location": f"{latitude}, {longitude}"
            }
            
            try:
                response = requests.post(f"{API_URL}/api/events", json=data)
                if response.status_code == 200:
                    st.success("✅ Report submitted successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to submit report")
            except:
                st.error("❌ Could not connect to server")

# ============================================
# PAGE: ALERTS
# ============================================
elif page == "🚨 Alerts":
    st.subheader("🚨 Real-time Alerts")
    
    alerts = fetch_alerts()
    
    if alerts:
        for alert in alerts:
            severity = alert.get('severity', 'low')
            if severity == 'high':
                st.error(f"🔴 **{alert.get('type')}** - {alert.get('location')}")
            elif severity == 'medium':
                st.warning(f"🟡 **{alert.get('type')}** - {alert.get('location')}")
            else:
                st.info(f"🔵 **{alert.get('type')}** - {alert.get('location')}")
    else:
        st.success("✅ No active alerts!")

# ============================================
# PAGE: ANALYTICS
# ============================================
elif page == "📈 Analytics":
    st.subheader("📊 Analytics Dashboard")
    
    events = fetch_events()
    
    if events:
        df = pd.DataFrame(events)
        
        # Object Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Object Distribution")
            all_objects = []
            for obj_list in df['objects']:
                if isinstance(obj_list, list):
                    all_objects.extend(obj_list)
            
            if all_objects:
                obj_counts = pd.Series(all_objects).value_counts()
                fig = px.bar(obj_counts, title="Objects Detected")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Defect Distribution")
            all_defects = []
            for def_list in df['road_defects']:
                if isinstance(def_list, list):
                    all_defects.extend(def_list)
            
            if all_defects:
                def_counts = pd.Series(all_defects).value_counts()
                fig = px.pie(values=def_counts.values, names=def_counts.index, title="Road Defects")
                st.plotly_chart(fig, use_container_width=True)
        
        # Daily Trend
        st.subheader("📈 Daily Trend")
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_counts = df.groupby('date').size().reset_index(name='count')
        fig = px.line(daily_counts, x='date', y='count', title="Events per Day")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No events found. Add some events first!")

# ============================================
# PAGE: REPORTS (Authority Only)
# ============================================
elif page == "📄 Reports":
    st.subheader("📄 Reports")
    
    report_type = st.selectbox("Select Report Type", ["Summary Report", "Defect Report", "Object Report"])
    
    if st.button("📥 Generate Report"):
        try:
            response = requests.get(f"{API_URL}/api/reports/{report_type.lower().replace(' ', '_')}")
            if response.status_code == 200:
                st.json(response.json())
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(response.json(), indent=2),
                    file_name=f"{report_type.lower().replace(' ', '_')}.json",
                    mime="application/json"
                )
        except:
            st.error("❌ Could not generate report")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption(f"🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")