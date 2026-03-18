#!/usr/bin/env python3
"""
Ultra Simple Arduino Test
Minimal test to debug connection issues
"""

import serial
import serial.tools.list_ports
import time

def main():
    print("=== Ultra Simple Arduino Test ===")
    print("This will show exactly what's happening with your Arduino")
    print()
    
    # Step 1: Check if pyserial works
    try:
        import serial
        print("✅ pyserial imported successfully")
    except ImportError:
        print("❌ pyserial not installed")
        print("Run: pip install pyserial")
        return
    
    # Step 2: List all ports
    print("\n📡 Scanning for serial ports...")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ NO SERIAL PORTS FOUND!")
        print("\nPossible causes:")
        print("- Arduino not connected via USB")
        print("- USB drivers not installed")
        print("- USB cable is charge-only")
        print("- Arduino not powered")
        return
    
    print(f"Found {len(ports)} ports:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device} - {port.description}")
    
    # Step 3: Test each port
    print("\n🔌 Testing each port...")
    
    for port in ports:
        print(f"\nTesting {port.device}...")
        
        try:
            # Try to open port
            ser = serial.Serial(
                port=port.device,
                baudrate=9600,
                timeout=3,
                write_timeout=3
            )
            print(f"  ✅ Port opened successfully")
            
            # Wait a moment
            time.sleep(2)
            
            # Check if there's any data
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
                print(f"  📨 Received: '{data}'")
            else:
                print(f"  ⚠️ No data waiting (Arduino might be silent)")
            
            # Try to send something
            ser.write(b'Hello Arduino\n')
            time.sleep(1)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
                print(f"  📤 Response: '{response}'")
            else:
                print(f"  ⚠️ No response to Hello")
            
            # Close port
            ser.close()
            print(f"  ✅ Port closed successfully")
            
            # If we got here, this port works!
            print(f"\n🎉 SUCCESS! {port.device} is working!")
            print(f"\nNext steps:")
            print(f"1. Run: python simple_bridge.py --port {port.device}")
            print(f"2. Open your website")
            print(f"3. Scan your RFID card")
            return
            
        except serial.SerialException as e:
            print(f"  ❌ Serial error: {e}")
        except Exception as e:
            print(f"  ❌ Other error: {e}")
    
    print(f"\n❌ NO WORKING PORTS FOUND!")
    print(f"\nTroubleshooting:")
    print(f"1. Check Arduino is connected and powered (LED on)")
    print(f"2. Close Arduino IDE completely")
    print(f"3. Install Arduino drivers")
    print(f"4. Try different USB cable")
    print(f"5. Try different USB port")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test stopped")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Try running as Administrator")
