# Network Monitoring Dashboard

A comprehensive network monitoring dashboard built with Streamlit to track and visualize campus LAN health. This application provides real-time monitoring of network devices, performance metrics tracking, and detailed analytics for maintaining optimal network performance.

## Table of Contents
- [VirtualBox Setup](#virtualbox-setup)
- [Installation Process](#installation-process)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Scope and Limitations](#scope-and-limitations)

## VirtualBox Setup

### 1. Creating Ubuntu VM
1. Download VirtualBox from [virtualbox.org](https://www.virtualbox.org/)
2. Download Ubuntu 22.04 LTS ISO from [ubuntu.com](https://ubuntu.com/download/desktop)
3. In VirtualBox Manager:
   - Click "New"
   - Name: NetworkMonitor
   - Type: Linux
   - Version: Ubuntu (64-bit)

### 2. VM Configuration
Recommended settings:
- Memory (RAM): 4GB minimum
- CPU: 2 cores minimum
- Storage: 20GB minimum
- Network Adapter: Bridged Adapter (for direct network access)

### 3. Network Setup
1. Open VM Settings > Network
2. Adapter 1:
   - Enable Network Adapter: checked
   - Attached to: Bridged Adapter
   - Name: Your physical network interface
3. Port Forwarding (if using NAT):
   - Protocol: TCP
   - Host Port: 5000
   - Guest Port: 5000

### 4. Install VirtualBox Guest Additions
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y build-essential linux-headers-$(uname -r)

# Insert Guest Additions CD and mount it
sudo mount /dev/cdrom /mnt
cd /mnt
sudo ./VBoxLinuxAdditions.run
```

## Installation Process

### 1. System Setup
```bash
# Update system and install required packages
sudo apt update
sudo apt install -y python3 python3-pip git

# Verify Python installation
python3 --version
python3 -m pip install --upgrade pip
```

### 2. Project Setup
```bash
# Clone the project
git clone <repository-url>
cd network-monitoring-dashboard

# Install project dependencies
pip install -r requirements.txt
```

### 3. Application Configuration
```bash
# Create streamlit config directory
mkdir -p ~/.streamlit

# Create config file
cat > ~/.streamlit/config.toml << EOF
[server]
headless = true
address = "0.0.0.0"
port = 5000
EOF
```

## Running the Application

### 1. Manual Run
```bash
# Start the application
cd ~/network-monitoring-dashboard
streamlit run main.py
```

### 2. Service Setup (Optional)
```bash
# Create service file
sudo tee /etc/systemd/system/network-monitor.service << EOF
[Unit]
Description=Network Monitoring Dashboard
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/network-monitoring-dashboard
ExecStart=/home/$USER/.local/bin/streamlit run main.py --server.port=5000 --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable network-monitor
sudo systemctl start network-monitor
```

## Troubleshooting

### VirtualBox-Specific Issues

1. Network Connectivity
```bash
# Check network interface
ip addr show

# Test internet connectivity
ping -c 4 8.8.8.8

# If using bridged adapter, verify network settings
sudo systemctl status networking
```

2. Port Forwarding Issues
```bash
# Check if application is listening
sudo netstat -tulpn | grep 5000

# Verify firewall settings
sudo ufw status
sudo ufw allow 5000/tcp
```

3. Guest Additions Problems
```bash
# Verify Guest Additions installation
lsmod | grep vboxguest

# Reinstall if needed
sudo apt install --reinstall virtualbox-guest-utils virtualbox-guest-x11
```

4. Common Problems and Solutions
- **Can't access dashboard from host:**
  - Verify port forwarding settings in VirtualBox
  - Check VM's IP address: `ip addr show`
  - Test local access: `curl localhost:5000`

- **Performance issues:**
  - Increase VM RAM and CPU allocation
  - Enable hardware virtualization in BIOS
  - Update VirtualBox Guest Additions

- **Network adapter not working:**
  - Try different adapter types (Bridged, NAT)
  - Restart network service: `sudo systemctl restart networking`
  - Check host network interface status

### Application Issues

1. Database Access
```bash
# Verify database file permissions
ls -l network_monitor.db
chmod 644 network_monitor.db
```

2. Application Startup
```bash
# Check service status
systemctl status network-monitor

# View application logs
journalctl -u network-monitor -f
```

3. Python Environment
```bash
# Verify Python packages
pip list | grep streamlit

# Check Python path
which python3
which streamlit
```


## Scope and Limitations

### Scope

1. **Network Monitoring Capabilities**
   - Real-time monitoring of network devices via ICMP (ping)
   - Support for multiple device types (servers, switches, routers, workstations)
   - Custom monitoring thresholds for different metrics
   - Historical data tracking and trend analysis

2. **Performance Metrics**
   - Response time (RTT)
   - Packet loss percentage
   - Network jitter
   - Device availability/uptime
   - Moving averages and trend analysis

3. **Device Management**
   - Add, edit, and remove network devices
   - Device categorization and tagging
   - Custom threshold configuration per device
   - Bulk device management

4. **Data Visualization**
   - Real-time performance graphs
   - Historical trend charts
   - Custom time range selection (6-72 hours)
   - Interactive dashboard components

5. **Reporting Features**
   - CSV data export
   - PDF report generation
   - Customizable metrics display
   - Threshold violation tracking

### Limitations

1. **Technical Constraints**
   - Limited to ICMP-based monitoring (ping)
   - No support for SNMP or other advanced protocols
   - Maximum recommended devices: 100 per instance
   - Data retention period: 30 days by default

2. **Security Considerations**
   - Basic authentication only
   - No built-in encryption for stored data
   - No role-based access control
   - Limited to internal network monitoring

3. **Performance Boundaries**
   - Minimum polling interval: 60 seconds
   - Maximum recommended concurrent devices: 100
   - Chart refresh rate: 60 seconds
   - Database size limit: 10GB

4. **Monitoring Restrictions**
   - No automated device discovery
   - No support for IPv6 addresses
   - Limited protocol support (ICMP only)
   - No built-in alerting system

5. **Deployment Constraints**
   - Single instance deployment only
   - No built-in clustering support
   - Limited to Ubuntu Linux environments
   - Requires persistent database storage
