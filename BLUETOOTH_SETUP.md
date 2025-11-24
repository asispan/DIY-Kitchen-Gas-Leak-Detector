# 🔵 Bluetooth Audio Setup Guide

## Quick Setup

### Step 1: Setup Bluetooth Audio Device
Run this interactive setup **once** to configure your Bluetooth speaker/headphones:

```bash
cd /home/zero2w1
./bluetooth_connect.py --setup
```

**Follow the prompts:**
1. Put your Bluetooth device in pairing mode
2. Wait for scan to complete (~20 seconds)
3. Select your device from the list
4. Device will be paired, connected, and saved for auto-connect

### Step 2: Start the System
```bash
sudo systemctl start gas-sensor-monitor.service
```

## What Happens on Boot

1. **Bluetooth connects automatically** to your configured device
2. **Gas sensor monitor starts** with audio alerts enabled
3. **Web interface becomes available** at http://10.0.0.221:5000

## Audio Alerts

When gas is detected:
- 🚨 **Continuous alarm** plays until gas clears
- 🔴 **Visual alerts** on web interface
- 💡 **Status LED** turns on (if connected)
- 📝 **Logging** of all events

When gas clears:
- ✅ **Clear sound** plays once
- 🟢 **Visual status** returns to safe
- 💡 **Status LED** turns off

## Testing Audio

Test your audio setup:
1. Visit: http://10.0.0.221:5000/api/test-audio
2. You should hear a warning beep through your Bluetooth device

## Manual Commands

```bash
# Check Bluetooth connection
./bluetooth_connect.py

# Setup new device
./bluetooth_connect.py --setup

# Check Bluetooth service status
sudo systemctl status bluetooth-connect.service

# Check main app status
sudo systemctl status gas-sensor-monitor.service

# View audio logs
tail -f logs/bluetooth.log
tail -f logs/gas_sensor.log
```

## Available Sound Files

- `gas_alert.wav` - Urgent alarm (continuous during gas detection)
- `gas_warning.wav` - Single warning beep  
- `startup.wav` - System startup sound
- `clear.wav` - Gas cleared notification

## Troubleshooting

### Bluetooth Issues
- Make sure device is in pairing mode during setup
- Check `logs/bluetooth.log` for connection details
- Some devices need to be "trusted" manually

### Audio Issues  
- Verify PulseAudio is running: `pulseaudio --check -v`
- Check audio device: `pactl list short sinks`
- Test direct audio: `pactl play-sample bell-window-system`

### No Sound During Alerts
- Check web interface shows "Audio Enabled: true"
- Verify Bluetooth device is connected and active
- Test API endpoint: `/api/test-audio`

## Device Requirements

**Compatible Bluetooth Audio Devices:**
- Bluetooth speakers with A2DP support
- Bluetooth headphones/earbuds
- Bluetooth-enabled soundbars

**Connection Process:**
- Automatic pairing and connection on boot
- Persistent connection maintained
- Auto-reconnect if connection drops
