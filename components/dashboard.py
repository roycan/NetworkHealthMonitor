import streamlit as st
from utils import format_response_time, calculate_uptime
from components.charts import create_response_time_chart, create_status_chart

def render_dashboard(database, monitor):
    st.title("Network Monitoring Dashboard")
    
    # Get all devices
    devices = database.get_devices()
    if not devices:
        st.warning("No devices configured. Add devices in the Device Manager.")
        return

    # Create metrics grid
    cols = st.columns(len(devices))
    for idx, device in enumerate(devices):
        with cols[idx]:
            history = database.get_device_history(device['id'], limit=100)
            latest = history[0] if history else None
            
            st.metric(
                label=device['ip_address'],
                value="Online" if (latest and latest['status']) else "Offline",
                delta=format_response_time(latest['response_time']) if latest else "N/A",
                delta_color="inverse"
            )
            
            uptime = calculate_uptime(history)
            st.progress(uptime/100, f"Uptime: {uptime:.1f}%")

    # Detailed device views
    for device in devices:
        with st.expander(f"Details: {device['ip_address']} - {device['description']}"):
            history = database.get_device_history(device['id'], limit=100)
            
            # Device info
            st.markdown(f"**Tags:** {', '.join(device['tags'] if device['tags'] else [])}")
            
            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    create_response_time_chart(history),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    create_status_chart(history),
                    use_container_width=True
                )
