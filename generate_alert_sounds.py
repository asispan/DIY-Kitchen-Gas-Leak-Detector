#!/usr/bin/env python3
"""
Generate alert sound files for gas detection
"""
import numpy as np
import wave
import struct

def generate_beep(frequency=800, duration=1.0, volume=0.7, sample_rate=44100):
    """Generate a beep sound"""
    frames = int(duration * sample_rate)
    wavedata = []
    
    for i in range(frames):
        # Generate sine wave
        value = volume * np.sin(frequency * 2 * np.pi * i / sample_rate)
        # Convert to 16-bit PCM and clamp
        data = max(-32767, min(32767, int(value * 32767)))
        wavedata.append([data, data])  # stereo
    
    return wavedata

def generate_urgent_alarm(duration=2.0, sample_rate=44100):
    """Generate urgent alternating alarm sound"""
    frames = int(duration * sample_rate)
    wavedata = []
    
    # Alternating frequencies for urgent sound
    freq1, freq2 = 1000, 800
    switch_rate = 0.2  # switch every 0.2 seconds
    
    for i in range(frames):
        time = i / sample_rate
        # Switch frequency based on time
        frequency = freq1 if (time % (switch_rate * 2)) < switch_rate else freq2
        
        # Generate sine wave with some modulation
        value = 0.6 * np.sin(frequency * 2 * np.pi * time)  # Reduced volume
        # Add slight tremolo effect
        tremolo = 1 + 0.2 * np.sin(8 * 2 * np.pi * time)  # Reduced tremolo
        value *= tremolo
        
        # Convert to 16-bit PCM and clamp
        data = max(-32767, min(32767, int(value * 16000)))  # Reduced amplitude
        wavedata.append([data, data])  # stereo
    
    return wavedata

def save_wav(filename, wavedata, sample_rate=44100):
    """Save wave data to file"""
    with wave.open(filename, 'w') as wav_file:
        # 2 channels (stereo), 2 bytes per sample (16-bit), sample rate
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for frame in wavedata:
            wav_file.writeframes(struct.pack('<hh', frame[0], frame[1]))

def main():
    print("Generating alert sound files...")
    
    # Generate different alert sounds
    sounds = {
        'gas_alert.wav': generate_urgent_alarm(duration=3.0),
        'gas_warning.wav': generate_beep(frequency=1000, duration=1.0),
        'startup.wav': generate_beep(frequency=600, duration=0.5, volume=0.4),
        'clear.wav': generate_beep(frequency=400, duration=0.3, volume=0.5)
    }
    
    for filename, wavedata in sounds.items():
        filepath = f"/home/zero2w1/sounds/{filename}"
        save_wav(filepath, wavedata)
        print(f"Created: {filepath}")
    
    print("Alert sound generation complete!")

if __name__ == "__main__":
    main()
