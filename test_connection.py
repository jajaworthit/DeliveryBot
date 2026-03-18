#!/usr/bin/env python3
"""
Simple Arduino Connection Test
Tests basic serial connection to Arduino
"""

import serial
import serial.tools.list_ports
import time

def test_connection():
    print("🔍 Arduino Connection Test")
    print("=" * 40)
    
    # 1. List available ports
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found!")
        print("   - Check USB connection")
        print("   - Install Arduino drivers")
        return
    
    print("📡 Available ports:")
    for i, port in enumerate(ports, 1):
        print(f"   {i}. {port.device} - {port.description}")
    
    print()
    
    # 2. Try each port
    for port in ports:
        print(f"🔌 Testing {port.device}...")
        
        try:
            # Try to open the port
            ser = serial.Serial(
                port=port.device,
                baudrate=9600,
                timeout=2
            )
            
            print(f"   ✅ Port opened successfully")
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Try to read any data
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    print(f"   📨 Received: {data}")
                else:
                    print(f"   ⚠️ Port open but no data received")
            else:
                print(f"   ⚠️ Port open but no data waiting")
            
            # Try to send a command
            ser.write(b'STATUS\n')
            time.sleep(1)
            
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"   📤 Response to STATUS: {response}")
            else:
                print(f"   ⚠️ No response to STATUS command")
            
            ser.close()
            print(f"   ✅ Test completed for {port.device}")
            print()
            
        except serial.SerialException as e:
            print(f"   ❌ Serial error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 40)

def check_arduino_specific():
    """Check for Arduino-specific ports"""
    print("\n🎯 Arduino-specific check:")
    
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        desc = port.description.lower()
        if 'arduino' in desc or 'ch340' in desc or 'cp210' in desc:
            print(f"   🎯 Found Arduino: {port.device} - {port.description}")
            
            # Try this port specifically
            try:
                ser = serial.Serial(port.device, 9600, timeout=3)
                time.sleep(3)  # Wait longer for Arduino
                
                # Read any startup messages
                while ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"      📨 Arduino says: {line}")
                
                ser.close()
                print(f"   ✅ Arduino test successful!")
                return port.device
                
            except Exception as e:
                print(f"   ❌ Arduino test failed: {e}")
    
    return None

if __name__ == "__main__":
    print("=== Simple Arduino Connection Test ===")
    print("This will help diagnose Arduino connection issues")
    print()
    
    # Test all ports
    test_connection()
    
    # Arduino-specific check
    arduino_port = check_arduino_specific()
    
    if arduino_port:
        print(f"\n🎉 SUCCESS! Arduino found on {arduino_port}")
        print(f"Run the bridge with: python arduino_bridge.py --port {arduino_port}")
    else:
        print(f"\n❌ No Arduino detected")
        print(f"Troubleshooting:")
        print(f"1. Check USB cable connection")
        print(f"2. Make sure Arduino is powered (LED on)")
        print(f"3. Install Arduino drivers")
        print(f"4. Close Arduino IDE Serial Monitor")
        print(f"5. Try different USB port")
