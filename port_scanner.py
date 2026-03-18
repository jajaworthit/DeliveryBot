#!/usr/bin/env python3
"""
COM Port Scanner for Arduino Connection
Lists available serial ports to help find the correct Arduino port
"""

import serial.tools.list_ports
import serial
import time

def scan_ports():
    """Scan for available serial ports"""
    print("🔍 Scanning for available serial ports...")
    print()
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found!")
        print("Make sure Arduino is connected and drivers are installed.")
        return
    
    print("📡 Available Serial Ports:")
    print("-" * 50)
    
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Manufacturer: {port.manufacturer}")
        
        # Try to identify if it might be an Arduino
        if 'arduino' in port.description.lower() or 'ch340' in port.description.lower():
            print(f"   🎯 Likely Arduino device!")
        elif 'usb' in port.description.lower() or 'cp210' in port.description.lower():
            print(f"   🔌 Possible USB device")
        
        print()
    
    print("-" * 50)
    print("💡 Tips:")
    print("• Arduino Uno/Mega: Usually COM3-COM5 on Windows")
    print("• Arduino Nano: Usually COM3-COM7 on Windows") 
    print("• Check Device Manager if unsure")
    print("• Make sure only one program uses the port")
    print()

def test_port_connection(port_name):
    """Test if we can connect to a specific port"""
    print(f"🔌 Testing connection to {port_name}...")
    
    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=9600,
            timeout=2
        )
        
        # Test if we can read from Arduino
        time.sleep(2)
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(f"✅ Connected! Received: {data}")
                ser.close()
                return True
        
        ser.close()
        print(f"❌ Port {port_name} is available but no data received")
        print("   (Arduino might not be sending data)")
        return False
        
    except serial.SerialException as e:
        print(f"❌ Failed to connect to {port_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error with {port_name}: {e}")
        return False

def interactive_test():
    """Interactive port testing"""
    ports = serial.tools.list_ports.comports()
    available_ports = [port.device for port in ports]
    
    if not available_ports:
        print("❌ No serial ports available!")
        return
    
    print("🎮 Enter port number to test (or 'all' to test all):")
    
    while True:
        choice = input("\n> ").strip().lower()
        
        if choice == 'quit' or choice == 'q':
            break
        elif choice == 'all':
            print(f"\n🔄 Testing all {len(available_ports)} ports...")
            for port in available_ports:
                test_port_connection(port)
                print("-" * 30)
        elif choice.isdigit():
            port_num = int(choice)
            if 1 <= port_num <= len(available_ports):
                port_name = available_ports[port_num - 1]
                test_port_connection(port_name)
            else:
                print(f"❌ Invalid port number! Choose 1-{len(available_ports)}")
        else:
            print("❌ Invalid choice! Enter port number or 'all'")

if __name__ == "__main__":
    print("=== Arduino COM Port Scanner ===")
    print("This tool helps find the correct Arduino serial port")
    print()
    
    scan_ports()
    
    try:
        interactive_test()
    except KeyboardInterrupt:
        print("\n👋 Scanner stopped by user")
