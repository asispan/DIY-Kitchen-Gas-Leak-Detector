#!/bin/bash

echo "MQ-135 Gas Sensor and Camera Monitor Installation Script"
echo "======================================================="

# Update system
echo "Updating system packages..."
sudo apt update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-venv libcamera-apps python3-picamera2 python3-opencv pigpio
sudo apt install -y python3-flask python3-gpiozero python3-socketio python3-eventlet python3-psutil

# Install Flask-SocketIO
echo "Installing Flask-SocketIO..."
pip3 install --break-system-packages flask-socketio

# Enable services
echo "Enabling services..."
sudo systemctl enable ssh
sudo systemctl enable pigpio
sudo systemctl enable gas-sensor-monitor.service

# Create logs directory
mkdir -p /home/zero2w1/logs

# Set permissions
chmod +x gas_sensor_app.py

echo "Installation completed!"
echo "The web interface is available at: http://$(hostname -I | awk '{print $1}'):5000"
echo "Service status: sudo systemctl status gas-sensor-monitor.service"
