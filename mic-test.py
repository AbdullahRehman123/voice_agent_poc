#!/usr/bin/env python3
"""
Microphone Diagnostic Tool
Helps identify why your microphone isn't working
"""

import sounddevice as sd
import sys

def diagnose_microphone():
    """Run comprehensive microphone diagnostics."""
    
    print("\n" + "="*60)
    print("🔍 MICROPHONE DIAGNOSTIC TOOL")
    print("="*60)
    
    # Step 1: Check if any devices are available
    print("\n[Step 1] Checking for audio devices...")
    print("-" * 60)
    
    try:
        devices = sd.query_devices()
        print(f"✅ Found {len(devices)} total audio devices\n")
    except Exception as e:
        print(f"❌ Error querying devices: {e}")
        return
    
    # Step 2: List all input devices
    print("\n[Step 2] Available INPUT devices:")
    print("-" * 60)
    
    input_devices = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append(i)
            is_default = " ⭐ [DEFAULT]" if i == sd.default.device[0] else ""
            print(f"\n  [{i}]{is_default}")
            print(f"    Name: {device['name']}")
            print(f"    Channels: {device['max_input_channels']}")
            print(f"    Sample Rate: {device['default_samplerate']} Hz")
            print(f"    Host API: {sd.query_hostapis(device['hostapi'])['name']}")
    
    if not input_devices:
        print("\n❌ NO INPUT DEVICES FOUND!")
        print("\nPossible solutions:")
        print("  1. Connect a microphone or headset")
        print("  2. Enable microphone in system settings")
        print("  3. Check privacy/permissions settings")
        return
    
    print(f"\n✅ Found {len(input_devices)} input device(s)")
    
    # Step 3: Check default device
    print("\n[Step 3] Testing DEFAULT microphone:")
    print("-" * 60)
    
    try:
        default_input = sd.default.device[0]
        default_device = sd.query_devices(default_input)
        print(f"Default device: {default_device['name']}")
    except Exception as e:
        print(f"❌ Error getting default device: {e}")
        default_input = None
    
    # Step 4: Test each input device
    print("\n[Step 4] Testing each input device:")
    print("-" * 60)
    print("You will have 2 seconds to speak into your microphone for each test.")
    print("Please say something like 'testing one two three'")
    
    for device_id in input_devices:
        device_info = sd.query_devices(device_id)
        print(f"\n📍 Testing Device [{device_id}]: {device_info['name']}")
        
        input("\n  Press ENTER to start 2-second recording...")
        print("  🎤 RECORDING NOW - SPEAK!")
        
        try:
            # Record with this specific device
            duration = 2
            samplerate = int(device_info['default_samplerate'])
            
            recording = sd.rec(
                int(duration * samplerate),
                samplerate=samplerate,
                channels=1,
                device=device_id,
                dtype='float32'
            )
            sd.wait()
            
            # Analyze the recording
            import numpy as np
            max_vol = np.abs(recording).max()
            avg_vol = np.abs(recording).mean()
            
            print(f"\n  📊 Results:")
            print(f"     Max amplitude: {max_vol:.6f}")
            print(f"     Avg amplitude: {avg_vol:.6f}")
            
            if max_vol > 0.01:
                print(f"  ✅ SUCCESS! This microphone is working!")
            elif max_vol > 0.001:
                print(f"  ⚠️  Weak signal - microphone works but very quiet")
            else:
                print(f"  ❌ No sound detected on this device")
                
        except Exception as e:
            print(f"  ❌ Error testing this device: {e}")
    
    # Step 5: Recommendations
    print("\n" + "="*60)
    print("💡 RECOMMENDATIONS:")
    print("="*60)
    print("""
1. If NO devices showed sound:
   • Check if microphone is muted in system settings
   • Check privacy permissions (especially on Mac/Windows)
   • Try a different microphone/headset
   • Restart your audio service/computer

2. If a device OTHER than default worked:
   • Change your system's default microphone
   • Or specify the working device in your code:
     sd.default.device = DEVICE_NUMBER

3. On Mac:
   • System Settings → Privacy & Security → Microphone
   • Make sure Terminal/Python has permission

4. On Windows:
   • Settings → Privacy → Microphone
   • Make sure apps can access microphone

5. On Linux:
   • Check with: arecord -l
   • May need to configure PulseAudio/ALSA
    """)
    print("="*60 + "\n")

def quick_permission_test():
    """Quick test to see if we can even access the microphone."""
    print("\n🔒 Testing microphone permissions...")
    
    try:
        # Try to open the default input device
        test = sd.rec(100, samplerate=16000, channels=1, device=None)
        sd.wait()
        print("✅ Microphone access granted!")
        return True
    except Exception as e:
        print(f"❌ Cannot access microphone: {e}")
        print("\nThis might be a permission issue!")
        return False

if __name__ == "__main__":
    print("\n🎙️  MICROPHONE DIAGNOSTICS")
    print("="*60)
    print("\nThis tool will help identify why your microphone isn't working.")
    print("Make sure your microphone is connected and unmuted!\n")
    
    # Quick permission check
    if not quick_permission_test():
        print("\n⚠️  Permission denied. Please check your system settings.")
        sys.exit(1)
    
    try:
        diagnose_microphone()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)