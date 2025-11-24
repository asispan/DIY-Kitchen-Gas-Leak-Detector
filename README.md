<div align="center">

# 🔥 DIY Kitchen Gas Leak Detector

**AI-Powered Gas Detection System with ElevenLabs Voice Alerts**

[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-AI%20Voice-6B4FBB)](https://elevenlabs.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202W-C51A4A?logo=raspberry-pi&logoColor=white)](https://www.raspberrypi.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

*An intelligent gas leak detection system featuring airplane-style AI voice readouts, real-time monitoring, and live camera streaming*

[Features](#-features) • [Hardware](#-hardware-requirements) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-endpoints)

</div>

---

## 📋 Overview

This project transforms a Raspberry Pi Zero 2W into an intelligent gas leak detector with professional-grade voice alerts powered by ElevenLabs AI. Inspired by aircraft warning systems, it provides clear, audible notifications for various system states including gas detection, system status, and camera monitoring.

## ✨ Features

- 🎤 **AI Voice Alerts** - ElevenLabs-generated airplane-style voice notifications
- 🔍 **Real-time Gas Detection** - MQ-135 sensor monitoring via GPIO
- 📹 **Live Camera Streaming** - Pi Camera or USB camera support with web streaming
- 🌐 **Web Dashboard** - Real-time monitoring interface with Socket.IO
- 📊 **System Metrics** - CPU, memory, temperature, and network monitoring
- 🔄 **Auto-start Service** - Systemd integration for automatic startup
- 🔐 **SSH Management** - Automatic SSH service control
- 📝 **Comprehensive Logging** - Detailed system and event logging
- 🔊 **Bluetooth Audio** - Support for Bluetooth speakers (Echo Dot compatible)

## 🛠️ Hardware Requirements

| Component | Description | Notes |
|-----------|-------------|-------|
| **Raspberry Pi Zero 2W** | Main controller | Tested on Raspbian Bookworm |
| **MQ-135 Gas Sensor** | Air quality/gas detection | Digital output to GPIO17 |
| **Pi Camera / USB Camera** | Video monitoring | Optional but recommended |
| **Power Supply** | 5V 2.5A minimum | Ensure stable power |
| **Optional: LED** | Status indicator | GPIO18 |
| **Optional: Bluetooth Speaker** | Audio output | For voice alerts |

### 🔌 Wiring Diagram

```
MQ-135 Gas Sensor:
├─ VCC  → 3.3V (Pin 1)
├─ GND  → GND (Pin 6)
└─ DOUT → GPIO17 (Pin 11)

Optional LED:
└─ LED  → GPIO18 (Pin 12)
```

## 🚀 Installation

### Quick Install

```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

#### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-flask \
    python3-gpiozero \
    python3-socketio \
    python3-eventlet \
    python3-psutil \
    python3-picamera2 \
    python3-opencv \
    libcamera-apps \
    pigpio
```

#### 2. Install Python Packages

```bash
pip3 install --break-system-packages flask-socketio
```

#### 3. Configure Bluetooth (Optional)

Copy the example configuration:
```bash
cp bluetooth_config.json.example bluetooth_config.json
```

Edit with your device details:
```json
{
  "target_device": "XX:XX:XX:XX:XX:XX",
  "device_name": "Your-Bluetooth-Device"
}
```

#### 4. Enable System Service

```bash
sudo cp gas-sensor-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gas-sensor-monitor.service
sudo systemctl start gas-sensor-monitor.service
```

## 📱 Usage

### Web Dashboard

Access the monitoring dashboard:
```
http://<raspberry-pi-ip>:5000
```

### Service Management

```bash
# Start service
sudo systemctl start gas-sensor-monitor.service

# Stop service
sudo systemctl stop gas-sensor-monitor.service

# Restart service
sudo systemctl restart gas-sensor-monitor.service

# Check status
sudo systemctl status gas-sensor-monitor.service

# View logs
sudo journalctl -u gas-sensor-monitor.service -f
```

### Manual Operation

```bash
cd /home/zero2w1
python3 gas_sensor_app.py
```

## 🌐 API Endpoints

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard interface |
| `/api/status` | GET | Current system and sensor status (JSON) |
| `/api/camera-feed` | GET | Current camera frame (base64) |
| `/api/health-check` | GET | System health information |
| `/api/test-voice` | GET | Test voice alert system |
| `/video_feed` | GET | Live MJPEG video stream |

### WebSocket Events

- `connect` - Client connection established
- `disconnect` - Client disconnection
- `status_update` - Real-time sensor status updates
- `camera_frame` - Live camera frame updates

### Example API Calls

```bash
# Get system status
curl http://<raspberry-pi-ip>:5000/api/status | python3 -m json.tool

# Get camera feed
curl http://<raspberry-pi-ip>:5000/api/camera-feed

# Health check
curl http://<raspberry-pi-ip>:5000/api/health-check
```

## 📁 Project Structure

```
/home/zero2w1/
├── gas_sensor_app.py          # Main application
├── requirements.txt            # Python dependencies
├── install.sh                  # Installation script
├── bluetooth_config.json       # Bluetooth configuration (not tracked)
├── bluetooth_config.json.example # Example config
├── templates/
│   └── index.html             # Web dashboard
├── static/                     # Static assets
├── logs/
│   └── gas_sensor.log         # Application logs
└── sounds/                     # Voice alert audio files
```

## ⚙️ Configuration

### Application Settings

Edit `gas_sensor_app.py` to customize:

```python
# Web server
HOST = '0.0.0.0'
PORT = 5000

# GPIO pins
GAS_SENSOR_PIN = 17
LED_PIN = 18

# Sensor settings
BOUNCE_TIME = 0.1  # Debounce time in seconds
```

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check service logs
sudo journalctl -u gas-sensor-monitor.service -n 50

# Verify GPIO permissions
sudo usermod -a -G gpio zero2w1

# Check if port is in use
sudo netstat -tlnp | grep :5000
```

### Camera Not Working

```bash
# Check camera detection
vcgencmd get_camera

# Test camera manually
libcamera-hello --list-cameras

# For USB cameras
ls -l /dev/video*
```

### GPIO Permissions

```bash
sudo usermod -a -G gpio $USER
# Logout and login again
```

## 🎙️ ElevenLabs Voice Generation

This project uses **ElevenLabs** AI-powered text-to-speech for generating realistic voice alerts. The alerts are designed to mimic professional aircraft warning systems for clarity and urgency.

### Voice Alert Types

- 🚨 Gas leak detected
- ✅ System normal
- 🔄 System starting
- 🎥 Camera status updates
- ⚠️ System warnings

To regenerate voice alerts, use the included script:
```bash
python3 generate_alert_sounds.py
```

## ⚠️ Important Notes

- ⚡ Ensure adequate power supply (minimum 2.5A recommended)
- 🌡️ Monitor system temperature to prevent throttling
- 🔌 Use 3.3V VCC for MQ-135 sensor (not 5V)
- 🧪 Calibrate MQ-135 sensor in clean air before use
- 🔐 Secure your Raspberry Pi if exposed to network

## 📊 System Requirements

- **OS**: Raspbian Bookworm (Debian 12)
- **Python**: 3.11+
- **RAM**: Minimum 512MB (Zero 2W has 512MB)
- **Storage**: 8GB+ SD card recommended

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ElevenLabs](https://elevenlabs.io/) - AI voice generation technology
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Socket.IO](https://socket.io/) - Real-time communication
- [gpiozero](https://gpiozero.readthedocs.io/) - GPIO control library

---

<div align="center">

*Created by Asis Panda on September 2025 | Version 1.0*

</div>
