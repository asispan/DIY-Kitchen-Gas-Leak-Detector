#!/bin/bash

echo "🚀 Gas Sensor System Startup Script"
echo "===================================="

LOG_FILE="/home/zero2w1/logs/startup.log"
mkdir -p /home/zero2w1/logs

# Function to log messages
log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function for voice announcements
announce() {
    local message="$1"
    echo "🔊 $message"
    espeak-ng -v hi -s 120 -g 8 -a 80 "$message" --stdout | aplay 2>/dev/null &
}

log_msg "=== SYSTEM STARTUP BEGINNING ==="

# 1. Check and start Bluetooth
log_msg "Checking Bluetooth service..."
if systemctl is-active --quiet bluetooth; then
    log_msg "✅ Bluetooth service is active"
else
    log_msg "❌ Starting Bluetooth service..."
    sudo systemctl start bluetooth
    sleep 2
fi

# 2. Check Bluetooth connection to Echo Dot
log_msg "Checking Echo Dot connection..."
if bluetoothctl info FC:49:2D:4C:13:81 | grep -q "Connected: yes"; then
    log_msg "✅ Echo Dot is connected"
    announce "Bluetooth audio connected"
else
    log_msg "⚠️  Echo Dot not connected - attempting reconnection..."
    bluetoothctl connect FC:49:2D:4C:13:81
    sleep 3
    
    if bluetoothctl info FC:49:2D:4C:13:81 | grep -q "Connected: yes"; then
        log_msg "✅ Echo Dot reconnected successfully"
        announce "Bluetooth audio reconnected"
    else
        log_msg "❌ Failed to connect to Echo Dot"
        announce "There is an issue with the Gas Sensor Bluetooth connection"
    fi
fi

# 3. Check SSH service
log_msg "Checking SSH service..."
if systemctl is-active --quiet ssh; then
    log_msg "✅ SSH service is active"
else
    log_msg "❌ Starting SSH service..."
    sudo systemctl start ssh
    announce "There is an issue with the Gas Sensor SSH service"
fi

# 4. Check camera hardware
log_msg "Checking camera hardware..."
if timeout 10 rpicam-hello --list-cameras 2>/dev/null | grep -q "ov5647"; then
    log_msg "✅ Pi Camera (OV5647) detected"
else
    log_msg "⚠️  Pi Camera not detected, will check USB cameras"
fi

# 5. Test PulseAudio for Bluetooth audio
log_msg "Testing audio system..."
if pulseaudio --check; then
    log_msg "✅ PulseAudio is running"
else
    log_msg "Starting PulseAudio..."
    pulseaudio --start
fi

# 6. Check gas sensor monitor service
log_msg "Checking gas sensor monitor service..."
if systemctl is-active --quiet gas-sensor-monitor; then
    log_msg "✅ Gas sensor monitor is active"
else
    log_msg "❌ Starting gas sensor monitor..."
    sudo systemctl start gas-sensor-monitor
    sleep 5
    
    if systemctl is-active --quiet gas-sensor-monitor; then
        log_msg "✅ Gas sensor monitor started successfully"
    else
        log_msg "❌ Failed to start gas sensor monitor"
        announce "There is an issue with the Gas Sensor service"
    fi
fi

# 7. Test web interface
log_msg "Testing web interface..."
sleep 10  # Give service time to fully start
if curl -s http://localhost:5000/api/status >/dev/null 2>&1; then
    log_msg "✅ Web interface is responding"
else
    log_msg "❌ Web interface is not responding"
    announce "There is an issue with the Gas Sensor web interface"
fi

# 8. Final system health summary
log_msg "=== STARTUP HEALTH SUMMARY ==="

BLUETOOTH_OK=$(bluetoothctl info FC:49:2D:4C:13:81 2>/dev/null | grep -q "Connected: yes" && echo "✅" || echo "❌")
SSH_OK=$(systemctl is-active --quiet ssh && echo "✅" || echo "❌") 
GAS_SERVICE_OK=$(systemctl is-active --quiet gas-sensor-monitor && echo "✅" || echo "❌")
WEB_OK=$(curl -s http://localhost:5000/api/status >/dev/null 2>&1 && echo "✅" || echo "❌")

log_msg "Bluetooth (Echo Dot): $BLUETOOTH_OK"
log_msg "SSH Service: $SSH_OK"
log_msg "Gas Sensor Service: $GAS_SERVICE_OK"  
log_msg "Web Interface: $WEB_OK"

# Overall health check
if [[ "$BLUETOOTH_OK" == "✅" && "$SSH_OK" == "✅" && "$GAS_SERVICE_OK" == "✅" && "$WEB_OK" == "✅" ]]; then
    log_msg "🎉 ALL SYSTEMS OPERATIONAL"
    announce "Gas sensor system is fully operational"
    exit 0
else
    log_msg "⚠️  SOME SYSTEMS HAVE ISSUES"
    announce "There is an issue with the Gas Sensor system"
    exit 1
fi

