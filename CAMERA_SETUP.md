# Camera Setup Guide

## Current Status
The system is currently running in **placeholder mode** because no camera is detected. The dashboard will display a placeholder image with instructions.

## Connecting a Camera

### Option 1: USB Webcam (Recommended)
1. Connect a USB webcam to any available USB port on the Raspberry Pi
2. Wait a few seconds for the device to be recognized
3. Restart the gas sensor service:
   ```bash
   sudo systemctl restart gas-sensor-monitor.service
   ```
4. Verify camera detection:
   ```bash
   sudo journalctl -u gas-sensor-monitor.service -n 50 | grep -i camera
   ```
5. Check the dashboard at http://10.0.0.221:5000 - you should see live video

### Option 2: Raspberry Pi Camera Module
**Note:** According to project notes, Pi Camera via PCIe has caused system crashes on Pi Zero 2W. Use USB camera instead unless you have a stable power supply and have tested it.

If you still want to try:
1. Connect the Pi Camera ribbon cable to the CSI port
   - Ensure the cable is fully inserted and the connector is locked
   - Blue side of cable faces the USB ports
2. Enable the camera interface:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Camera → Enable
   ```
3. Reboot:
   ```bash
   sudo reboot
   ```
4. After reboot, verify detection:
   ```bash
   rpicam-hello --list-cameras
   vcgencmd get_camera
   ```
5. If detected, restart the service:
   ```bash
   sudo systemctl restart gas-sensor-monitor.service
   ```

## Verifying Camera Operation

### Check Service Logs
```bash
sudo journalctl -u gas-sensor-monitor.service -f
```
Look for messages like:
- `✅ USB camera found at index X` (success)
- `✅ Pi Camera detected via libcamera` (success)
- `❌ No cameras available - enabling placeholder mode` (no camera)

### Test API Endpoint
```bash
curl -s http://10.0.0.221:5000/api/camera-feed | python3 -m json.tool
```
Check the response:
- `"available": true` means real camera is working
- `"available": false` means using placeholder mode

### View Dashboard
Open http://10.0.0.221:5000 in a web browser
- With camera: You'll see live video feed
- Without camera: You'll see the placeholder image with instructions

## Troubleshooting

### USB Camera Not Detected
1. Check USB connection:
   ```bash
   lsusb
   ```
   You should see a camera device listed

2. Check for video devices:
   ```bash
   ls -l /dev/video*
   ```

3. Test with fswebcam:
   ```bash
   sudo apt install fswebcam
   fswebcam -d /dev/video0 test.jpg
   ```

### Pi Camera Not Detected
1. Check hardware:
   - Reseat the ribbon cable
   - Inspect for damage
   - Ensure quality 5V/3A power supply

2. Check firmware detection:
   ```bash
   vcgencmd get_camera
   rpicam-hello --list-cameras
   ```

3. Test capture:
   ```bash
   rpicam-still -o test.jpg
   ```

### Power Issues
The MQ-135 gas sensor draws significant power (~5W when heated). If using both sensor and camera:
- Use a quality 5V/3A power supply
- Consider using the sensor at 3.3V instead of 5V
- Monitor for voltage drops: `vcgencmd get_throttled`

## System Status
- **Gas Sensor**: ✅ Working on GPIO17
- **Dashboard**: ✅ Running at http://10.0.0.221:5000
- **Camera**: ⚠️ Placeholder mode (no hardware connected)
- **SSH**: ✅ Enabled
- **Web Service**: ✅ Operational

## Related Files
- Main application: `/home/zero2w1/gas_sensor_app.py`
- Service unit: `/etc/systemd/system/gas-sensor-monitor.service`
- Logs: `/home/zero2w1/logs/gas_sensor.log`
- Troubleshooting: `CAMERA_TROUBLESHOOTING.md`
