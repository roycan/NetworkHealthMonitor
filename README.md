# Network Monitoring Dashboard

A comprehensive network monitoring dashboard built with Streamlit to track and visualize campus LAN health. This application provides real-time monitoring of network devices, performance metrics tracking, and detailed analytics for maintaining optimal network performance.

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation Process](#installation-process)
  - [System Packages](#system-packages)
  - [Python Setup](#python-setup)
  - [Project Setup](#project-setup)
  - [Database Setup](#database-setup)
- [User Account Configuration](#user-account-configuration)
  - [Installation User Types](#installation-user-types)
  - [Permission Management](#permission-management)
  - [Environment Setup](#environment-setup)
- [PATH Configuration](#path-configuration)
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

# Create data directory (will be customized based on user type)
sudo mkdir -p /var/lib/network-monitor
```

## User Account Configuration

### Installation User Types

#### 1. Root User
Not recommended for security reasons. If you must use root:
```bash
# Set proper ownership and permissions
chown root:root /var/lib/network-monitor
chmod 755 /var/lib/network-monitor
```

#### 2. System Service User (Recommended)
Create a dedicated service user:
```bash
# Create service user
sudo useradd -r -s /bin/false network-monitor

# Set ownership
sudo chown network-monitor:network-monitor /var/lib/network-monitor
sudo chown -R network-monitor:network-monitor /path/to/network-monitoring-dashboard

# Set permissions
sudo chmod 755 /var/lib/network-monitor
```

#### 3. Regular User
For installation under a regular user account:
```bash
# Set ownership
sudo chown $USER:$USER /var/lib/network-monitor
sudo chown -R $USER:$USER /path/to/network-monitoring-dashboard

# Set permissions
sudo chmod 755 /var/lib/network-monitor
```

### Permission Management

#### Directory Structure Permissions
```bash
# Application directory
sudo chmod -R 755 /path/to/network-monitoring-dashboard

# Data directory
sudo chmod 755 /var/lib/network-monitor

# Database file
sudo chmod 644 /var/lib/network-monitor/network_monitor.db

# Log directory
sudo mkdir -p /var/log/network-monitor
sudo chown $SERVICE_USER:$SERVICE_USER /var/log/network-monitor
sudo chmod 755 /var/log/network-monitor
```

#### Configuration Files
```bash
# Service configuration
sudo chmod 644 /etc/systemd/system/network-monitor.service

# Application configuration
sudo chmod 644 /path/to/network-monitoring-dashboard/.streamlit/config.toml
```

### Environment Setup

#### 1. System Service User
Create environment file:
```bash
sudo tee /etc/default/network-monitor << EOF
# Application Environment
PYTHONPATH=/path/to/network-monitoring-dashboard
SQLITE_DB_PATH=/var/lib/network-monitor/network_monitor.db
PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin

# User-specific settings
HOME=/home/network-monitor
USER=network-monitor
EOF
```

#### 2. Regular User
Add to user's profile (~/.profile or ~/.bashrc):
```bash
# Application Environment
export PYTHONPATH=/path/to/network-monitoring-dashboard
export SQLITE_DB_PATH=/var/lib/network-monitor/network_monitor.db
```

### Database Setup
Initialize the SQLite database with proper permissions:
```bash
# Create database
sqlite3 /var/lib/network-monitor/network_monitor.db ".databases"

# Set ownership and permissions
sudo chown $SERVICE_USER:$SERVICE_USER /var/lib/network-monitor/network_monitor.db
sudo chmod 644 /var/lib/network-monitor/network_monitor.db
```

## Service Setup
Create and configure the systemd service with user-specific settings:
```bash
sudo tee /etc/systemd/system/network-monitor.service << EOF
[Unit]
Description=Network Monitoring Dashboard
After=network.target

[Service]
# User Configuration
User=network-monitor
Group=network-monitor

# Directory Configuration
WorkingDirectory=/path/to/network-monitoring-dashboard

# Environment Configuration
EnvironmentFile=/etc/default/network-monitor

# Execution
ExecStart=/usr/local/bin/streamlit run main.py --server.port=5000 --server.address=0.0.0.0

# Security
NoNewPrivileges=yes
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes

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
sudo -u network-monitor sqlite3 /var/lib/network-monitor/network_monitor.db ".tables"

# Check device table
sudo -u network-monitor sqlite3 /var/lib/network-monitor/network_monitor.db "SELECT * FROM devices;"
```

### 5. Monitor Resource Usage
```bash
# Check CPU and memory usage
top -p $(pgrep -f streamlit)
```

## Troubleshooting

### Service Issues
- Check service status: `sudo systemctl status network-monitor`
- View logs: `sudo journalctl -u network-monitor -f`
- Verify service user: `ps -ef | grep streamlit`

### Permission Issues
- Check file ownership: `ls -l /var/lib/network-monitor/network_monitor.db`
- Check directory permissions: `ls -ld /var/lib/network-monitor`
- Verify user access: `sudo -u network-monitor ls -l /var/lib/network-monitor`

### Database Issues
- Check database permissions: `ls -l /var/lib/network-monitor/network_monitor.db`
- Verify database access: `sudo -u network-monitor sqlite3 /var/lib/network-monitor/network_monitor.db ".tables"`
- Check write permissions: `sudo -u network-monitor touch /var/lib/network-monitor/test`

### Environment Issues
- Check service environment: `sudo systemctl show network-monitor -p Environment`
- Verify PATH: `sudo -u network-monitor echo $PATH`
- Test streamlit access: `sudo -u network-monitor which streamlit`
