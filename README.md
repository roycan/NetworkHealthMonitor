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
sudo apt install -y python3 python3-pip python3-venv sqlite3 build-essential python3-dev
```

### Python Setup
Set up Python environment with proper permissions:
```bash
# Verify Python installation
python3 --version

# Update pip to latest version
python3 -m pip install --upgrade pip --no-cache-dir

# Configure pip to use system certificate store
pip config set global.cert /etc/ssl/certs/ca-certificates.crt
```

### Project Setup
Clone and set up the project:
```bash
# Clone the project
git clone <repository-url>
cd network-monitoring-dashboard

# Install project dependencies with recommended flags
pip install --no-cache-dir -r requirements.txt --use-pep517 --no-warn-script-location

# Create data directory
mkdir -p /var/lib/network-monitor
sudo chown ubuntu:ubuntu /var/lib/network-monitor
```

### Managing pip Warnings
Common pip warnings and their solutions:

1. **DEPRECATION Warning**:
   - Use `--use-pep517` flag during installation
   - Keep pip updated using `python3 -m pip install --upgrade pip`

2. **Script Location Warning**:
   - Use `--no-warn-script-location` flag during installation
   - Or add local bin directory to PATH: `export PATH="$HOME/.local/bin:$PATH"`

3. **Cache Warnings**:
   - Use `--no-cache-dir` flag to prevent cache-related issues
   - Clear pip cache if needed: `pip cache purge`

4. **SSL Certificate Warnings**:
   - Configure pip to use system certificate store as shown in Python Setup
   - Install required SSL certificates: `sudo apt install ca-certificates`

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
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/ubuntu/.local/bin"
Environment="PYTHONPATH=/home/ubuntu/network-monitoring-dashboard"
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
- Verify Python environment: `python3 -m pip list`
- Clear pip cache: `pip cache purge`
- Restart service: `sudo systemctl restart network-monitor`
