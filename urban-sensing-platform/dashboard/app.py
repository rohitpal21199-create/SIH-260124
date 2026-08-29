"""
URBAN SENSING PLATFORM - WEB DASHBOARD
Complete Dashboard for Authorities
"""

import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime
import json

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Urban Sensing Dashboard",
    page_icon="🚍",
    layout="wide"
)

# ============================================
# API CONFIG
# ============================================
API_URL = "http://localhost:8000"

# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_stats():
    try:
        response = requests.get(f"{API_URL}/api/stats")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

@st.cache_data(ttl=10)
def fetch_events():
    try:
        response = requests.get(f"{API_URL}/api/events")
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=10)
def fetch_alerts():
    try:
        response = requests.get(f"{API_URL}/api/alerts")
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=10)
def fetch_reports():
    try:
        response = requests.get(f"{API_URL}/api/reports/summary")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

# ============================================
# HEADER
# ============================================
st.title("🚍 Urban Sensing Platform - Dashboard")
st.markdown(f"🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("📊 Navigation")
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
    with col1:
        st.metric("📊 Total Events", stats.get('total_events', 0))
    with col2:
        st.metric("📦 Objects Detected", stats.get('total_objects', 0))
    with col3:
        st.metric("🛑 Road Defects", stats.get('total_defects', 0))
    with col4:
        st.metric("🚌 Active Buses", stats.get('unique_buses', 0))
    
    st.markdown("---")
    
    st.subheader("📋 Recent Events")
    events = fetch_events()
    if events:
        df = pd.DataFrame(events[-20:])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No events found")

# ============================================
# PAGE: GIS MAP
# ============================================
elif page == "🗺️ GIS Map":
    st.subheader("🗺️ GIS Map View")
    
    events = fetch_events()
    
    m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)
    
    for event in events[-100:]:
        try:
            lat, lon = map(float, event.get('location', '0,0').split(','))
            
            if event.get('road_defects'):
                color = 'red'
                icon = 'exclamation-triangle'
            elif event.get('objects'):
                color = 'blue'
                icon = 'bus'
            else:
                color = 'green'
                icon = 'info-circle'
            
            folium.Marker(
                [lat, lon],
                popup=f"{event.get('road_defects', ['Event'])[0]}<br>{event.get('timestamp')[:16]}",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)
        except:
            continue
    
    st_folium(m, width=900, height=600)

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
        st_folium(m, width=900, height=600)
    else:
        st.info("No defects found")

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
        
        st.subheader("📈 Daily Trend")
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_counts = df.groupby('date').size().reset_index(name='count')
        fig = px.line(daily_counts, x='date', y='count', title="Events per Day")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available")

# ============================================
# PAGE: REPORTS
# ============================================
elif page == "📄 Reports":
    st.subheader("📄 Reports")
    
    report_type = st.selectbox("Select Report Type", ["Summary Report", "Defect Report", "Object Report"])
    
    if st.button("📥 Generate Report"):
        try:
            response = requests.get(f"{API_URL}/api/reports/summary")
            if response.status_code == 200:
                report = response.json()
                st.json(report)
                
                # Download button
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(report, indent=2),
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