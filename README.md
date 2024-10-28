# Network Monitoring Dashboard

A comprehensive network monitoring dashboard built with Streamlit to track and visualize campus LAN health. This application provides real-time monitoring of network devices, performance metrics tracking, and detailed analytics for maintaining optimal network performance.

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation Process](#installation-process)
  - [System Packages](#system-packages)
  - [Python Setup](#python-setup)
  - [Project Setup](#project-setup)
  - [Database Setup](#database-setup)
- [Directory Permissions](#directory-permissions)
  - [Application Files](#application-files)
  - [Data Directory](#data-directory)
  - [Log Directory](#log-directory)
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
Set up Python environment:
```bash
# Verify Python installation
python3 --version

# Update pip to latest version
python3 -m pip install --upgrade pip
```

### Project Setup
Clone and set up the project:
```bash
# Clone the project
git clone <repository-url>
cd network-monitoring-dashboard

# Install project dependencies
pip install -r requirements.txt

# Create necessary directories
sudo mkdir -p /var/lib/network-monitor
sudo mkdir -p /var/log/network-monitor
```

## Directory Permissions

### Application Files
Set correct permissions for application files:
```bash
# Set ownership for application directory
sudo chown -R network-monitor:network-monitor /path/to/network-monitoring-dashboard
sudo chmod -R 755 /path/to/network-monitoring-dashboard

# Protect configuration files
sudo chmod 644 /path/to/network-monitoring-dashboard/.streamlit/config.toml
sudo chmod 644 /path/to/network-monitoring-dashboard/requirements.txt

# Ensure executable permissions for Python files
sudo chmod 755 /path/to/network-monitoring-dashboard/main.py
sudo chmod 755 /path/to/network-monitoring-dashboard/*.py
```

### Data Directory
Configure data directory permissions:
```bash
# Set ownership for data directory
sudo chown network-monitor:network-monitor /var/lib/network-monitor
sudo chmod 755 /var/lib/network-monitor

# Set database file permissions
sudo chmod 644 /var/lib/network-monitor/network_monitor.db
```

### Log Directory
Set up log directory permissions:
```bash
# Set ownership for log directory
sudo chown network-monitor:network-monitor /var/log/network-monitor
sudo chmod 755 /var/log/network-monitor

# Ensure logs are writable
sudo chmod 644 /var/log/network-monitor/*.log
```

### Validate Permissions
Run these commands to verify permissions are set correctly:
```bash
# Check application directory
ls -la /path/to/network-monitoring-dashboard

# Check data directory
ls -la /var/lib/network-monitor

# Check log directory
ls -la /var/log/network-monitor

# Verify service user can access everything
sudo -u network-monitor ls -la /path/to/network-monitoring-dashboard
sudo -u network-monitor ls -la /var/lib/network-monitor
sudo -u network-monitor ls -la /var/log/network-monitor
```

## Service Setup
Create and configure the systemd service:
```bash
sudo tee /etc/systemd/system/network-monitor.service << EOF
[Unit]
Description=Network Monitoring Dashboard
After=network.target

[Service]
Type=simple
User=network-monitor
Group=network-monitor
WorkingDirectory=/path/to/network-monitoring-dashboard
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="SQLITE_DB_PATH=/var/lib/network-monitor/network_monitor.db"
ExecStart=/usr/local/bin/streamlit run main.py --server.port=5000 --server.address=0.0.0.0

# Security settings
NoNewPrivileges=yes
ProtectSystem=full
ReadWritePaths=/var/lib/network-monitor /var/log/network-monitor
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF

# Set correct permissions for service file
sudo chmod 644 /etc/systemd/system/network-monitor.service

# Reload and restart service
sudo systemctl daemon-reload
sudo systemctl restart network-monitor
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

### 3. Verify File Permissions
```bash
# Check application files
ls -la /path/to/network-monitoring-dashboard/*.py

# Check data directory
ls -la /var/lib/network-monitor

# Check log directory
ls -la /var/log/network-monitor
```

### 4. Test Service User Access
```bash
# Test application access
sudo -u network-monitor python3 -c "import sys; print(sys.path)"

# Test data directory access
sudo -u network-monitor touch /var/lib/network-monitor/test_write
sudo -u network-monitor rm /var/lib/network-monitor/test_write

# Test log directory access
sudo -u network-monitor touch /var/log/network-monitor/test_write
sudo -u network-monitor rm /var/log/network-monitor/test_write
```

## Troubleshooting

### Permission Issues
- Check file ownership: `ls -l /var/lib/network-monitor/network_monitor.db`
- Check directory permissions: `ls -ld /var/lib/network-monitor`
- Verify user access: `sudo -u network-monitor ls -l /var/lib/network-monitor`
- Check SELinux context: `ls -Z /var/lib/network-monitor` (if SELinux is enabled)

### Common Permission Problems
1. Database access denied:
   ```bash
   sudo chown network-monitor:network-monitor /var/lib/network-monitor/network_monitor.db
   sudo chmod 644 /var/lib/network-monitor/network_monitor.db
   ```

2. Log writing failed:
   ```bash
   sudo chown -R network-monitor:network-monitor /var/log/network-monitor
   sudo chmod 755 /var/log/network-monitor
   sudo chmod 644 /var/log/network-monitor/*.log
   ```

3. Application files not executable:
   ```bash
   sudo chmod 755 /path/to/network-monitoring-dashboard/main.py
   sudo chmod 755 /path/to/network-monitoring-dashboard/*.py
   ```

### Verify Service Environment
```bash
# Check service environment variables
sudo systemctl show network-monitor -p Environment

# Test streamlit accessibility
sudo -u network-monitor which streamlit

# Verify Python path
sudo -u network-monitor python3 -c "import sys; print(sys.path)"
```
