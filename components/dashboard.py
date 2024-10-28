import streamlit as st
from datetime import datetime
from utils import format_response_time, calculate_uptime
from components.charts import (
    create_response_time_chart, create_status_chart,
    create_detailed_metrics_chart, create_trend_chart
)
from components.export import export_device_data_csv, export_device_report_pdf
import base64

def get_download_link(data, filename, text):
    """Generate a download link for the data"""
    if isinstance(data, str):
        # For CSV (string data)
        b64 = base64.b64encode(data.encode()).decode()
    else:
        # For PDF (binary data)
        b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def render_dashboard(database, monitor):
    st.title("Network Monitoring Dashboard")
    
    # Get all devices
    devices = database.get_devices()
    if not devices:
        st.warning("No devices configured. Add devices in the Device Manager.")
        return

    # Time range selector for trends
    trend_hours = st.selectbox(
        "Trend Analysis Time Range",
        options=[6, 12, 24, 48, 72],
        index=2,
        format_func=lambda x: f"Last {x} hours"
    )

    # Create metrics grid
    cols = st.columns(len(devices))
    for idx, device in enumerate(devices):
        with cols[idx]:
            history = database.get_device_history(device['id'], limit=100)
            latest = history[0] if history else None
            
            # Show device type and status
            st.markdown(f"**{device['device_type']}**")
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
        with st.expander(f"Details: {device['ip_address']} - {device['description']} ({device['device_type']})"):
            try:
                history = database.get_device_history(device['id'], limit=100)
                trends = database.get_device_trends(device['id'], hours=trend_hours)
                
                # Add export buttons in a row
                col1, col2, _ = st.columns([1, 1, 2])
                
                # Export CSV button
                with col1:
                    if st.button(f"Export CSV 📊", key=f"csv_{device['id']}"):
                        try:
                            csv_data = export_device_data_csv(database, device['id'], hours=trend_hours)
                            if csv_data:
                                filename = f"network_monitoring_{device['ip_address']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                st.markdown(get_download_link(csv_data, filename, "Download CSV"), unsafe_allow_html=True)
                            else:
                                st.error("Failed to generate CSV export")
                        except Exception as e:
                            st.error(f"Error exporting CSV: {str(e)}")
                
                # Export PDF button
                with col2:
                    if st.button(f"Export PDF 📑", key=f"pdf_{device['id']}"):
                        try:
                            pdf_data = export_device_report_pdf(database, device['id'], hours=trend_hours)
                            if pdf_data:
                                filename = f"network_monitoring_{device['ip_address']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                st.markdown(get_download_link(pdf_data, filename, "Download PDF"), unsafe_allow_html=True)
                            else:
                                st.error("Failed to generate PDF export")
                        except Exception as e:
                            st.error(f"Error exporting PDF: {str(e)}")
                
                # Device info
                st.markdown(f"**Tags:** {', '.join(device['tags'] if device['tags'] else [])}")
                
                if latest := (history[0] if history else None):
                    # Current metrics with threshold indicators
                    metrics_cols = st.columns(4)
                    with metrics_cols[0]:
                        response_time = latest['response_time']
                        threshold = device['response_time_threshold']
                        st.metric(
                            "Response Time",
                            format_response_time(response_time),
                            delta=f"Threshold: {format_response_time(threshold)}",
                            delta_color="inverse" if threshold and response_time > threshold else "off"
                        )
                    
                    with metrics_cols[1]:
                        packet_loss = latest['packet_loss']
                        threshold = device['packet_loss_threshold']
                        st.metric(
                            "Packet Loss",
                            f"{packet_loss:.1f}%",
                            delta=f"Threshold: {threshold:.1f}%" if threshold else None,
                            delta_color="inverse" if threshold and packet_loss > threshold else "off"
                        )
                    
                    with metrics_cols[2]:
                        jitter = latest['jitter']
                        threshold = device['jitter_threshold']
                        st.metric(
                            "Jitter",
                            format_response_time(jitter),
                            delta=f"Threshold: {format_response_time(threshold)}",
                            delta_color="inverse" if threshold and jitter > threshold else "off"
                        )
                    
                    # Show threshold violations if any
                    if latest['threshold_violations']:
                        st.warning(
                            "⚠️ Threshold Violations: " + 
                            ", ".join(v.replace('_', ' ').title() for v in latest['threshold_violations'])
                        )
                
                # Charts
                tab1, tab2 = st.tabs(["Real-time Metrics", "Trend Analysis"])
                
                with tab1:
                    st.plotly_chart(
                        create_detailed_metrics_chart(history, device),
                        use_container_width=True
                    )
                
                with tab2:
                    st.plotly_chart(
                        create_trend_chart(trends),
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error loading device details: {str(e)}")
