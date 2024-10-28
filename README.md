# Network Monitoring Dashboard

A comprehensive network monitoring dashboard built with Streamlit to track and visualize campus LAN health. This application provides real-time monitoring of network devices, performance metrics tracking, and detailed analytics for maintaining optimal network performance.

## Table of Contents
- [VirtualBox Setup](#virtualbox-setup)
- [Installation Process](#installation-process)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

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
