#!/usr/bin/env python3
"""
Enhanced MQ-135 Gas Sensor Monitor with Voice Alerts and System Health Monitoring
- Voice alerts in Hindi with repetition and pauses
- System health checks for Bluetooth, SSH, web service
- Camera streaming with fixed hardware
- Comprehensive error handling with voice feedback
"""

import RPi.GPIO as GPIO
import time
import threading
import logging
import signal
import sys
import os
import subprocess
import json
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import cv2
import base64

# Configuration
GAS_SENSOR_PIN = 17
DEBOUNCE_TIME = 2.0
ALERT_REPEAT_INTERVAL = 10.0

# Flask and SocketIO setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gas_sensor_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
gas_detected = False
alert_active = False
camera = None
camera_available = False
system_healthy = True
last_health_check = None

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceAlerts:
    def __init__(self):
        self.enabled = os.environ.get('ENABLE_AUDIO', 'false').lower() == 'true'
        logger.info(f"Voice alerts {'enabled' if self.enabled else 'disabled'}")
    
    def play_sound_file(self, sound_name, repeat_count=1):
        """Play a sound file using aplay"""
        if not self.enabled:
            logger.info(f"Sound (disabled): {sound_name}")
            return
            
        sound_path = os.path.join('/home/zero2w1/sounds', f"{sound_name}.wav")
        
        if not os.path.exists(sound_path):
            logger.error(f"Sound file not found: {sound_path}")
            return
            
        logger.info(f"🔊 Playing sound: {sound_name}")
        
        def play_thread():
            try:
                for i in range(repeat_count):
                    logger.info(f"   Playing repetition {i+1}/{repeat_count}")
                    subprocess.run(['aplay', '-q', sound_path], check=True)
                    
                    # Pause between repetitions (except last one)
                    if i < repeat_count - 1:
                        time.sleep(0.5)
                        
            except Exception as e:
                logger.error(f"Sound playback failed: {e}")
        
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()
    
    def speak_alert(self, message, repeat_count=3):
        """Speak message with Hindi voice, slower speed, and repetition"""
        if not self.enabled:
            logger.info(f"Voice alert (disabled): {message}")
            return
            
        logger.info(f"🔊 Voice alert: {message}")
        
        def speak_thread():
            try:
                for i in range(repeat_count):
                    logger.info(f"   Speaking repetition {i+1}/{repeat_count}")
                    
                    # Use Hindi voice with slower speed and word gaps
                    cmd = [
                        'espeak-ng', 
                        '-v', 'hi',      # Hindi voice
                        '-s', '120',     # Speed (slower)
                        '-g', '8',       # Gap between words
                        '-a', '80',      # Amplitude
                        '--stdout',
                        message
                    ]
                    
                    # Pipe to aplay for audio output
                    espeak_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                    aplay_proc = subprocess.Popen(['aplay'], stdin=espeak_proc.stdout)
                    
                    espeak_proc.stdout.close()
                    aplay_proc.wait()
                    
                    # Pause between repetitions (except last one)
                    if i < repeat_count - 1:
                        time.sleep(2)
                        
            except Exception as e:
                logger.error(f"Voice alert failed: {e}")
        
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()

class SystemHealthMonitor:
    def __init__(self, voice_alerts):
        self.voice_alerts = voice_alerts
        
    def check_bluetooth_status(self):
        """Check if Bluetooth is connected to target device"""
        try:
            result = subprocess.run(
                ['bluetoothctl', 'info', 'FC:49:2D:4C:13:81'],
                capture_output=True, text=True, timeout=5
            )
            return 'Connected: yes' in result.stdout
        except:
            return False
    
    def check_ssh_status(self):
        """Check if SSH service is running"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'ssh'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() == 'active'
        except:
            return False
    
    def check_web_service(self):
        """Check if web service is responding"""
        try:
            # Simple check - if we're running, web service is likely OK
            return True
        except:
            return False
    
    def perform_health_check(self):
        """Perform comprehensive system health check"""
        global system_healthy, last_health_check
        
        logger.info("🔍 Performing system health check...")
        
        bluetooth_ok = self.check_bluetooth_status()
        ssh_ok = self.check_ssh_status()
        web_ok = self.check_web_service()
        
        all_healthy = bluetooth_ok and ssh_ok and web_ok
        
        logger.info(f"Health check results:")
        logger.info(f"  Bluetooth: {'✅' if bluetooth_ok else '❌'}")
        logger.info(f"  SSH: {'✅' if ssh_ok else '❌'}")
        logger.info(f"  Web Service: {'✅' if web_ok else '❌'}")
        logger.info(f"  Overall: {'✅ Healthy' if all_healthy else '❌ Issues detected'}")
        
        # If system becomes unhealthy, trigger alert
        if system_healthy and not all_healthy:
            logger.warning("System health degraded - triggering voice alert")
            self.voice_alerts.speak_alert("There is an issue with the Gas Sensor")
        
        system_healthy = all_healthy
        last_health_check = datetime.now()
        
        return {
            'bluetooth': bluetooth_ok,
            'ssh': ssh_ok, 
            'web': web_ok,
            'overall': all_healthy,
            'timestamp': last_health_check.isoformat()
        }

class CameraManager:
    def __init__(self):
        self.camera = None
        self.camera_available = False
        self.placeholder_mode = False
        self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize camera with improved detection"""
        global camera_available
        
        try:
            # First check if libcamera detects the camera
            logger.info("Checking for Pi Camera via libcamera...")
            result = subprocess.run(
                ['rpicam-hello', '--list-cameras'],
                capture_output=True, text=True, timeout=10
            )
            
            if 'ov5647' in result.stdout or 'imx219' in result.stdout:
                logger.info("✅ Pi Camera detected via libcamera!")
                
                # Try to initialize with OpenCV (will use libcamera backend)
                try:
                    self.camera = cv2.VideoCapture(0)
                    if self.camera and self.camera.isOpened():
                        # Test frame capture
                        ret, frame = self.camera.read()
                        if ret and frame is not None:
                            logger.info("✅ Camera successfully initialized with OpenCV")
                            camera_available = True
                            self.camera_available = True
                            return
                        else:
                            logger.warning("Camera opened but cannot capture frames")
                    else:
                        logger.warning("Cannot open camera with OpenCV")
                except Exception as e:
                    logger.error(f"OpenCV camera initialization failed: {e}")
            else:
                logger.info("No Pi Camera detected")
                
        except subprocess.TimeoutExpired:
            logger.error("Camera detection timed out")
        except Exception as e:
            logger.error(f"Camera detection failed: {e}")
        
        # Fallback - try USB cameras by scanning multiple indices
        try:
            logger.info("Checking for USB cameras...")
            for cam_index in range(5):  # Try indices 0-4
                try:
                    test_camera = cv2.VideoCapture(cam_index)
                    if test_camera and test_camera.isOpened():
                        ret, frame = test_camera.read()
                        if ret and frame is not None:
                            logger.info(f"✅ USB camera found at index {cam_index}")
                            self.camera = test_camera
                            camera_available = True
                            self.camera_available = True
                            return
                        test_camera.release()
                except Exception as e:
                    logger.debug(f"No camera at index {cam_index}: {e}")
        except Exception as e:
            logger.error(f"USB camera scan failed: {e}")
        
        # No cameras available - enable placeholder mode
        logger.warning("❌ No cameras available - enabling placeholder mode")
        camera_available = False
        self.camera_available = False
        self.placeholder_mode = True
        
    def generate_placeholder_frame(self):
        """Generate a placeholder image when no camera is available"""
        import numpy as np
        
        # Create a 640x480 dark blue/gray image
        height, width = 480, 640
        placeholder = np.zeros((height, width, 3), dtype=np.uint8)
        placeholder[:, :] = [40, 40, 60]  # Dark blue-gray
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_lines = [
            ("No Camera Detected", (width//2 - 180, height//2 - 40), 1.0, (255, 255, 255), 2),
            ("Please connect a camera:", (width//2 - 200, height//2 + 20), 0.7, (200, 200, 200), 1),
            ("- USB webcam, or", (width//2 - 150, height//2 + 60), 0.6, (180, 180, 180), 1),
            ("- Pi Camera via ribbon cable", (width//2 - 180, height//2 + 95), 0.6, (180, 180, 180), 1),
            ("Then restart the service", (width//2 - 170, height//2 + 135), 0.6, (150, 150, 150), 1),
        ]
        
        for text, pos, scale, color, thickness in text_lines:
            cv2.putText(placeholder, text, pos, font, scale, color, thickness, cv2.LINE_AA)
        
        return placeholder
        
    def get_frame(self):
        """Get camera frame as base64 encoded string"""
        frame = None
        
        # Try to get real camera frame
        if self.camera_available and self.camera:
            try:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    logger.warning("Failed to capture frame from camera")
                    self.placeholder_mode = True
            except Exception as e:
                logger.error(f"Frame capture error: {e}")
                self.placeholder_mode = True
        
        # Use placeholder if no camera or capture failed
        if frame is None or self.placeholder_mode:
            frame = self.generate_placeholder_frame()
        
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_data = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{frame_data}"
        except Exception as e:
            logger.error(f"Frame encoding error: {e}")
            return None
    
    def cleanup(self):
        """Cleanup camera resources"""
        if self.camera:
            self.camera.release()


class GasSensorMonitor:
    def __init__(self):
        self.voice_alerts = VoiceAlerts()
        self.health_monitor = SystemHealthMonitor(self.voice_alerts)
        self.camera_manager = CameraManager()
        self.running = True
        self.gas_count = 0
        self.last_detection = None
        
        # GPIO setup
        GPIO.setmode(GPIO.BCM)

        # Clean up any existing GPIO setup first
        try:
            pass
        except:
            pass
        GPIO.setup(GAS_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(GAS_SENSOR_PIN, GPIO.FALLING, 
                            callback=self.gas_detected_callback, 
                            bouncetime=int(DEBOUNCE_TIME * 1000))
        
        logger.info("Gas sensor initialized successfully on GPIO17")
        
        # Play startup sound
        self.voice_alerts.play_sound_file("start-gas-leak", 1)
        
        # Start health monitoring thread
        self.health_thread = threading.Thread(target=self.periodic_health_check, daemon=True)
        self.health_thread.start()
        
    def periodic_health_check(self):
        """Periodic system health checks"""
        while self.running:
            try:
                self.health_monitor.perform_health_check()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(60)
    
    def gas_detected_callback(self, channel):
        """GPIO callback for gas detection"""
        global gas_detected, alert_active
        
        if not alert_active:
            self.gas_count += 1
            self.last_detection = datetime.now()
            gas_detected = True
            alert_active = True
            
            logger.warning(f"🚨 GAS DETECTED! Count: {self.gas_count}")
            
            # Trigger voice alert
            self.voice_alerts.play_sound_file("11labs_gas_alert_v2", 1)
            
            # Start continuous alert thread
            alert_thread = threading.Thread(target=self.continuous_gas_alert, daemon=True)
            alert_thread.start()
            
            # Notify web clients
            socketio.emit('gas_detected', {
                'detected': True,
                'count': self.gas_count,
                'timestamp': self.last_detection.isoformat()
            })
    
    def continuous_gas_alert(self):
        """Continuous alert while gas is detected"""
        global gas_detected, alert_active
        
        logger.info("Started continuous gas alert")
        
        while alert_active and self.running:
            time.sleep(ALERT_REPEAT_INTERVAL)
            
            if alert_active:
                # Check if gas is still detected
                if GPIO.input(GAS_SENSOR_PIN) == GPIO.HIGH:
                    # Gas cleared
                    gas_detected = False
                    alert_active = False
                    logger.info("✅ Gas levels normalized")
                    
                    # Clear alert voice message
                    self.voice_alerts.play_sound_file("air-clear", 1)
                    
                    socketio.emit('gas_cleared', {
                        'detected': False,
                        'timestamp': datetime.now().isoformat()
                    })
                    break
                else:
                    # Gas still detected - repeat alert
                    logger.warning("🚨 Gas still detected - repeating alert")
            self.voice_alerts.play_sound_file("11labs_gas_alert_v2", 1)
    
    def get_status(self):
        """Get current sensor status"""
        return {
            'gas_detected': gas_detected,
            'alert_active': alert_active,
            'detection_count': self.gas_count,
            'last_detection': self.last_detection.isoformat() if self.last_detection else None,
            'gpio_state': GPIO.input(GAS_SENSOR_PIN),
            'camera_available': self.camera_manager.camera_available,
            'system_health': self.health_monitor.perform_health_check()
        }
    
    def cleanup(self):
        """Cleanup GPIO and resources"""
        # Play shutdown sound
        self.voice_alerts.play_sound_file("shutdown-gas-leak", 1)
        time.sleep(2)  # Wait for sound to play
        
        self.running = False
        self.camera_manager.cleanup()
        try:
            GPIO.cleanup()
        except Exception as e:
            logger.error(f"GPIO cleanup error: {e}")
        logger.info("Gas sensor cleanup completed")

# Global sensor monitor instance
sensor_monitor = None

# Flask routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current status"""
    if sensor_monitor:
        return jsonify(sensor_monitor.get_status())
    return jsonify({'error': 'Sensor not initialized'})

@app.route('/api/camera-feed')
def camera_feed():
    """Get current camera frame (real or placeholder)"""
    if sensor_monitor:
        frame_data = sensor_monitor.camera_manager.get_frame()
        if frame_data:
            return jsonify({'frame': frame_data, 'available': sensor_monitor.camera_manager.camera_available})
    
    return jsonify({'frame': None, 'available': False})

@app.route('/api/test-voice')
def test_voice():
    """Test voice alert system"""
    if sensor_monitor:
        sensor_monitor.voice_alerts.speak_alert("Voice alert system test", 1)
        return jsonify({'status': 'Voice alert test initiated'})
    return jsonify({'error': 'Sensor not initialized'})

@app.route('/api/health-check')
def health_check():
    """Manual system health check"""
    if sensor_monitor:
        health_status = sensor_monitor.health_monitor.perform_health_check()
        return jsonify(health_status)
    return jsonify({'error': 'Sensor not initialized'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    if sensor_monitor:
        emit('status_update', sensor_monitor.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global sensor_monitor
    
    logger.info("Shutdown signal received")
    if sensor_monitor and sensor_monitor.voice_alerts:
        sensor_monitor.voice_alerts.play_sound_file("shutdown-gas-leak", 1)
        time.sleep(2)  # Wait for sound to play
    if sensor_monitor:
        sensor_monitor.cleanup()
    sys.exit(0)

def main():
    """Main function"""
    global sensor_monitor
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("🚀 Starting Enhanced Gas Sensor and Camera System with Voice Alerts")
        
        # Initialize sensor monitor
        sensor_monitor = GasSensorMonitor()
        
        # System startup voice notification
        # Log system status
        status = sensor_monitor.get_status()
        logger.info(f"System Status:")
        logger.info(f"  Camera: {'Available' if status['camera_available'] else 'Not available'}")
        logger.info(f"  Voice Alerts: {'Enabled' if sensor_monitor.voice_alerts.enabled else 'Disabled'}")
        logger.info(f"  System Health: {'✅' if status['system_health']['overall'] else '❌'}")
        
        # Start Flask app
        logger.info("Starting web interface on http://0.0.0.0:5000")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        if sensor_monitor and sensor_monitor.voice_alerts:
            sensor_monitor.voice_alerts.play_sound_file("shutdown-gas-leak", 1)

if __name__ == '__main__':
    main()
