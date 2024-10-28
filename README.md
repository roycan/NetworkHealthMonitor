# Network Monitoring Dashboard

A comprehensive network monitoring dashboard built with Streamlit to track and visualize campus LAN health. This application provides real-time monitoring of network devices, performance metrics tracking, and detailed analytics for maintaining optimal network performance.

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation Process](#installation-process)
  - [System Packages](#system-packages)
  - [Python Setup](#python-setup)
  - [Project Setup](#project-setup)
  - [Database Setup](#database-setup)
- [Service Setup](#service-setup)
- [Firewall Configuration](#firewall-configuration)
- [Testing Instructions](#testing-instructions)
- [Troubleshooting](#troubleshooting)

## System Requirements
- Ubuntu Linux 20.04 LTS or newer
- Python 3.10 or newer
- SQLite3 (usually pre-installed on Ubuntu)
- 2GB RAM minimum
- 10GB free disk space

## Installation Process

### System Packages
Update system and install required packages:
```bash
sudo apt update
sudo apt install -y python3 python3-pip sqlite3
```

### Python Setup
Verify Python installation and update pip:
```bash
# Verify Python installation
python3 --version
pip3 --version

# Update pip
pip3 install --upgrade pip
```

### Project Setup
Clone and set up the project:
```bash
# Clone the project
git clone <repository-url>
cd network-monitoring-dashboard

# Install project dependencies
pip3 install -r requirements.txt

# Create data directory
mkdir -p /var/lib/network-monitor
sudo chown ubuntu:ubuntu /var/lib/network-monitor
```

### Database Setup
Initialize the SQLite database:
```bash
# Initialize SQLite database
sqlite3 /var/lib/network-monitor/network_monitor.db ".databases"
```

## Service Setup
Create and configure the systemd service:
```bash
sudo tee /etc/systemd/system/network-monitor.service << EOF
[Unit]
Description=Network Monitoring Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/network-monitoring-dashboard
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
```

**Note:** Adjust the WorkingDirectory path to match the location where you cloned the repository. If you cloned it to a different location or using a different user, modify the path accordingly.

## Firewall Configuration
Configure the firewall to allow access to the dashboard:
```bash
# Allow Streamlit port
sudo ufw allow 5000/tcp

# Verify firewall status
sudo ufw status
```

## Testing Instructions

### 1. Verify Service Status
```bash
sudo systemctl status network-monitor
```

### 2. Check Application Logs
```bash
sudo journalctl -u network-monitor -f
```

### 3. Access Dashboard
- Open a web browser and navigate to: `http://your_server_ip:5000`
- Verify that you can see the dashboard and all metrics

### 4. Test Database
```bash
# Check if database exists and tables are created
sqlite3 /var/lib/network-monitor/network_monitor.db ".tables"

# Check device table
sqlite3 /var/lib/network-monitor/network_monitor.db "SELECT * FROM devices;"
```

### 5. Monitor Resource Usage
```bash
# Check CPU and memory usage
top -p $(pgrep -f streamlit)
```

## Troubleshooting
- Check service status: `sudo systemctl status network-monitor`
- View logs: `sudo journalctl -u network-monitor -f`
- Check database: `sqlite3 /var/lib/network-monitor/network_monitor.db ".tables"`
- Check file permissions: `ls -l /var/lib/network-monitor/network_monitor.db`
- Restart service: `sudo systemctl restart network-monitor`
