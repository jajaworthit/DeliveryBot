#!/usr/bin/env python3
"""
Arduino Diagnostic Tool
Comprehensive troubleshooting for Arduino connection issues
"""

import sys
import subprocess
import platform

def check_python_packages():
    """Check if required packages are installed"""
    print("🔍 Checking Python packages...")
    
    try:
        import serial
        print("   ✅ pyserial is installed")
        print(f"      Version: {serial.VERSION}")
    except ImportError:
        print("   ❌ pyserial NOT installed")
        print("      Fix: pip install pyserial")
        return False
    
    try:
        import websockets
        print("   ✅ websockets is installed")
    except ImportError:
        print("   ❌ websockets NOT installed")
        print("      Fix: pip install websockets")
        return False
    
    return True

def check_system_info():
    """Check system information"""
    print("\n💻 System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {sys.version}")
    
    # Check Windows-specific info
    if platform.system() == "Windows":
        try:
            result = subprocess.run(['wmic', 'path', 'win32_serialport', 'get', 'deviceid'], 
                              capture_output=True, text=True)
            if result.returncode == 0:
                print("   Windows COM ports detected:")
                for line in result.stdout.split('\n'):
                    if 'COM' in line and 'DeviceID' not in line:
                        print(f"      {line.strip()}")
        except:
            print("   Could not enumerate Windows COM ports")

def check_drivers():
    """Check for common Arduino drivers"""
    print("\n🔧 Checking Arduino Drivers...")
    
    if platform.system() == "Windows":
        try:
            # Check for CH340 driver (common Arduino clone)
            result = subprocess.run(['pnputil', '/e', 'oem*.inf'], 
                              capture_output=True, text=True)
            if 'ch340' in result.stdout.lower():
                print("   ✅ CH340 driver found")
            else:
                print("   ⚠️ CH340 driver not found")
                print("      May need to install for Arduino clones")
        except:
            print("   Could not check drivers")

def test_serial_imports():
    """Test serial functionality"""
    print("\n🧪 Testing Serial Functionality...")
    
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        
        print(f"   Found {len(ports)} serial ports")
        
        if not ports:
            print("   ❌ No serial ports available")
            print("      Causes:")
            print("      - Arduino not connected via USB")
            print("      - USB drivers not installed")
            print("      - USB cable faulty")
            return False
        
        for port in ports:
            print(f"   📡 {port.device}: {port.description}")
            
            # Test if we can create serial object
            try:
                test_ser = serial.Serial()
                test_ser.port = port.device
                print(f"      ✅ Can create serial object")
            except Exception as e:
                print(f"      ❌ Serial object error: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Serial import error: {e}")
        return False

def check_arduino_specific():
    """Check for Arduino-specific issues"""
    print("\n🎯 Arduino-Specific Checks:")
    
    # Check if Arduino IDE is running
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if 'arduino' in proc.info['name'].lower():
                print("   ⚠️ Arduino IDE is running")
                print("      Close Arduino IDE Serial Monitor!")
    except:
        print("   Could not check running processes")
    
    print("\n📋 Arduino Connection Checklist:")
    print("   [ ] Arduino connected via USB")
    print("   [ ] Arduino power LED is on")
    print("   [ ] Correct USB cable (data+power, not charge-only)")
    print("   [ ] Arduino IDE Serial Monitor closed")
    print("   [ ] No other program using COM port")
    print("   [ ] Drivers installed (CH340/CP210 for clones)")
    print("   [ ] Arduino code uploaded successfully")

def generate_fix_commands():
    """Generate specific fix commands"""
    print("\n🛠️ Automated Fix Commands:")
    print("\n1. Install missing packages:")
    print("   pip install pyserial websockets psutil")
    
    print("\n2. Test connection with specific port:")
    print("   python -c \"import serial; s=serial.Serial('COM3',9600); print('Connected!')\"")
    
    print("\n3. Run diagnostic:")
    print("   python test_connection.py")
    
    print("\n4. Try simple bridge:")
    print("   python simple_bridge.py --port COM3")

def main():
    print("=== Arduino Connection Diagnostic Tool ===")
    print("This will help identify why Arduino connection is failing")
    print()
    
    # Run all checks
    packages_ok = check_python_packages()
    check_system_info()
    check_drivers()
    serial_ok = test_serial_imports()
    check_arduino_specific()
    generate_fix_commands()
    
    print("\n" + "="*50)
    if packages_ok and serial_ok:
        print("🎯 DIAGNOSIS: Software looks OK")
        print("   Issue is likely hardware/connection related")
        print("   Check USB cable, drivers, and Arduino power")
    else:
        print("🎯 DIAGNOSIS: Software issue detected")
        print("   Install missing packages or fix Python environment")
    
    print("\n📞 Next Steps:")
    print("1. Run: python test_connection.py")
    print("2. If ports found, run: python simple_bridge.py --port COMX")
    print("3. Still failing? Check hardware connections")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Diagnostic stopped")
    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
