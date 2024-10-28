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

def render_deployment_instructions():
    st.header("Deployment Instructions for Ubuntu Linux")
    
    # System Requirements
    st.subheader("1. System Requirements")
    st.markdown("""
    - Ubuntu Linux 20.04 LTS or newer
    - Python 3.10 or newer
    - SQLite3 (usually pre-installed on Ubuntu)
    - 2GB RAM minimum
    - 10GB free disk space
    """)
    
    # Installation Process
    st.subheader("2. Step-by-Step Installation Process")
    st.markdown("#### Installing Required System Packages")
    st.code("""
sudo apt update
sudo apt install -y python3 python3-pip sqlite3
    """)
    
    st.markdown("#### Setting up Python and pip")
    st.code("""
# Verify Python installation
python3 --version
pip3 --version

# Update pip
pip3 install --upgrade pip
    """)
    
    st.markdown("#### Project Setup")
    st.code("""
# Clone the project
git clone <repository-url>
cd network-monitoring-dashboard

# Install project dependencies
pip3 install -r requirements.txt

# Create data directory
mkdir -p /var/lib/network-monitor
sudo chown ubuntu:ubuntu /var/lib/network-monitor
    """)
    
    st.markdown("#### Database Setup")
    st.code("""
# Initialize SQLite database
sqlite3 /var/lib/network-monitor/network_monitor.db ".databases"
    """)
    
    st.subheader("3. Service Setup")
    st.markdown("#### Creating systemd Service")
    st.code("""
sudo tee /etc/systemd/system/network-monitor.service << EOF
[Unit]
Description=Network Monitoring Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/network-monitoring-dashboard
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="SQLITE_DB_PATH=/var/lib/network-monitor/network_monitor.db"
ExecStart=/usr/local/bin/streamlit run main.py --server.port=5000 --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable network-monitor
sudo systemctl start network-monitor
    """)
    
    st.subheader("4. Firewall Configuration")
    st.code("""
# Allow Streamlit port
sudo ufw allow 5000/tcp

# Verify firewall status
sudo ufw status
    """)
    
    st.subheader("5. Testing Instructions")
    st.markdown("""
    1. **Verify Service Status:**
       ```bash
       sudo systemctl status network-monitor
       ```
    
    2. **Check Application Logs:**
       ```bash
       sudo journalctl -u network-monitor -f
       ```
    
    3. **Access Dashboard:**
       - Open a web browser and navigate to: `http://your_server_ip:5000`
       - Verify that you can see the dashboard and all metrics
    
    4. **Test Database:**
       ```bash
       # Check if database exists and tables are created
       sqlite3 /var/lib/network-monitor/network_monitor.db ".tables"
       
       # Check device table
       sqlite3 /var/lib/network-monitor/network_monitor.db "SELECT * FROM devices;"
       ```
    
    5. **Monitor Resource Usage:**
       ```bash
       # Check CPU and memory usage
       top -p $(pgrep -f streamlit)
       ```
    """)
    
    st.subheader("6. Troubleshooting")
    st.markdown("""
    - Check service status: `sudo systemctl status network-monitor`
    - View logs: `sudo journalctl -u network-monitor -f`
    - Check database: `sqlite3 /var/lib/network-monitor/network_monitor.db ".tables"`
    - Check file permissions: `ls -l /var/lib/network-monitor/network_monitor.db`
    - Restart service: `sudo systemctl restart network-monitor`
    """)

def render_dashboard(database, monitor):
    st.title("Network Monitoring Dashboard")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Device Manager", "Deployment Guide"])
    
    with tab1:
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

        # Detailed device sections
        for device in devices:
            st.markdown(f"### Device Details: {device['ip_address']} - {device['description']} ({device['device_type']})")
            with st.container():
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
                    chart_tabs = st.tabs(["Real-time Metrics", "Trend Analysis"])
                    
                    with chart_tabs[0]:
                        st.plotly_chart(
                            create_detailed_metrics_chart(history, device),
                            use_container_width=True
                        )
                    
                    with chart_tabs[1]:
                        st.plotly_chart(
                            create_trend_chart(trends),
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error loading device details: {str(e)}")
            
            st.markdown("---")  # Add separator between devices

    with tab2:
        from components.device_manager import render_device_manager
        render_device_manager(database)
    
    with tab3:
        render_deployment_instructions()

    # Auto-refresh every 60 seconds
    st.empty()
    st.markdown(
        """
        <meta http-equiv="refresh" content="60">
        """,
        unsafe_allow_html=True
    )
