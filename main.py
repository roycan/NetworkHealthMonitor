import streamlit as st
from database import Database
from monitoring import NetworkMonitor
from components.device_manager import render_device_manager
from components.dashboard import render_dashboard

# Page configuration
st.set_page_config(
    page_title="Network Monitoring Dashboard",
    page_icon="🌐",
    layout="wide"
)

# Initialize database and monitoring
@st.cache_resource
def init_resources():
    db = Database()
    monitor = NetworkMonitor(db)
    monitor.start_monitoring()
    return db, monitor

db, monitor = init_resources()

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "Device Manager"])

if page == "Dashboard":
    render_dashboard(db, monitor)
else:
    render_device_manager(db)

# Auto-refresh every 60 seconds
st.empty()
st.markdown(
    """
    <meta http-equiv="refresh" content="60">
    """,
    unsafe_allow_html=True
)
