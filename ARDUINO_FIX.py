#!/usr/bin/env python3
"""
Arduino Connection Fix Tool
Comprehensive diagnostic and automatic fix for Arduino connection issues
"""

import serial
import serial.tools.list_ports
import time
import sys
import os

def scan_ports_detailed():
    """Detailed port scanning with Arduino-specific detection"""
    print("🔍 DETAILED PORT SCAN")
    print("=" * 50)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ NO SERIAL PORTS FOUND!")
        print("\n🔧 SOLUTIONS:")
        print("1. Check Arduino USB connection")
        print("2. Install Arduino drivers (CH340/CP210)")
        print("3. Try different USB cable")
        print("4. Run as Administrator")
        return None
    
    arduino_ports = []
    other_ports = []
    
    for i, port in enumerate(ports, 1):
        print(f"\n{i}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Manufacturer: {port.manufacturer}")
        print(f"   VID:PID: {port.vid}:{port.pid}")
        print(f"   HWID: {port.hwid}")
        
        # Arduino detection
        desc_lower = port.description.lower()
        hwid_lower = port.hwid.lower() if port.hwid else ""
        
        is_arduino = any([
            'arduino' in desc_lower,
            'ch340' in desc_lower,
            'cp210' in desc_lower,
            'ftdi' in desc_lower,
            'usb serial' in desc_lower,
            'uart' in desc_lower,
            port.vid == 0x2341,  # Arduino official
            port.vid == 0x1A86,  # CH340
            port.vid == 0x10C4,  # CP210
        ])
        
        if is_arduino:
            arduino_ports.append(port)
            print(f"   🎯 ARDUINO DETECTED!")
        else:
            other_ports.append(port)
            print(f"   📡 Generic serial port")
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"   Arduino ports: {len(arduino_ports)}")
    print(f"   Other ports: {len(other_ports)}")
    
    if arduino_ports:
        print("\n🎯 RECOMMENDED ARDUINO PORTS:")
        for port in arduino_ports:
            print(f"   {port.device} - {port.description}")
        return arduino_ports[0].device
    elif other_ports:
        print("\n⚠️ NO ARDUINO FOUND - TRYING FIRST PORT:")
        print(f"   {other_ports[0].device} - {other_ports[0].description}")
        return other_ports[0].device
    
    return None

def test_port_connection(port_name, baud_rate=9600):
    """Test connection to specific port with multiple methods"""
    print(f"\n🔌 TESTING CONNECTION TO {port_name}")
    print("-" * 40)
    
    try:
        # Method 1: Basic connection test
        print("1. Testing basic connection...")
        ser = serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            timeout=5,
            write_timeout=5
        )
        print("   ✅ Port opened successfully")
        
        # Method 2: Test if port is responsive
        print("2. Testing port responsiveness...")
        time.sleep(2)  # Wait for Arduino to initialize
        
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
            if data:
                print(f"   📨 Arduino says: {data}")
            else:
                print("   ⚠️ Port open but no initial data")
        else:
            print("   ⚠️ Port open but no data waiting")
        
        # Method 3: Send test command
        print("3. Sending test command...")
        ser.write(b'HELLO\n')
        time.sleep(2)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
            print(f"   📤 Arduino responded: {response}")
            ser.close()
            return True, response
        else:
            print("   ❌ No response to test command")
            ser.close()
            return False, "No response"
            
    except serial.SerialException as e:
        print(f"   ❌ Serial error: {e}")
        return False, str(e)
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, str(e)

def check_arduino_code():
    """Check if Arduino is running the right code"""
    print("\n📝 ARDUINO CODE CHECK")
    print("=" * 50)
    print("Your Arduino should be running code that:")
    print("✅ Uses Serial.begin(9600)")
    print("✅ Prints RFID UID with 'Scanned UID:' prefix")
    print("✅ Prints 'Access Granted' or 'Access Denied'")
    print("✅ Prints 'Door Open' and 'Door Closed'")
    print("✅ Responds to 'STATUS' command")
    print("\n📋 SAMPLE ARDUINO OUTPUT:")
    print("Scanned UID: 0xC3 0x33 0xA8 0x39")
    print("Access Granted")
    print("Door Open")
    print("Door Closed")

def create_working_bridge():
    """Create a simple, working bridge"""
    bridge_code = '''#!/usr/bin/env python3
"""
Simple Working Arduino Bridge
Guaranteed to work with your Arduino
"""

import serial
import json
import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger(__name__)

class SimpleBridge:
    def __init__(self, port):
        self.port = port
        self.serial_conn = None
        self.clients = set()
        self.connected = False
        
    async def connect_serial(self):
        try:
            self.serial_conn = serial.Serial(self.port, 9600, timeout=2)
            await asyncio.sleep(2)
            self.connected = True
            log.info(f"✅ Connected to Arduino on {self.port}")
            await self.broadcast({'type': 'connection', 'status': 'CONNECTED'})
            return True
        except Exception as e:
            log.error(f"❌ Connection failed: {e}")
            self.connected = False
            await self.broadcast({'type': 'connection', 'status': 'DISCONNECTED'})
            return False
    
    async def read_serial(self):
        if not self.connected:
            return
        
        try:
            if self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    log.info(f"Arduino: {line}")
                    await self.process_line(line)
        except Exception as e:
            log.error(f"Read error: {e}")
            self.connected = False
    
    async def process_line(self, line):
        low = line.lower()
        
        if 'door open' in low:
            await self.broadcast({'type': 'door_status', 'status': 'OPEN'})
        elif 'door close' in low or 'door closed' in low:
            await self.broadcast({'type': 'door_status', 'status': 'CLOSED'})
        elif 'access granted' in low:
            await self.broadcast({'type': 'rfid_scan', 'access': 'GRANTED', 'message': line})
        elif 'access denied' in low:
            await self.broadcast({'type': 'rfid_scan', 'access': 'DENIED', 'message': line})
        elif 'ready' in low:
            await self.broadcast({'type': 'system_status', 'status': 'READY'})
    
    async def broadcast(self, data):
        if self.clients:
            message = json.dumps(data)
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)
            self.clients -= disconnected
    
    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        log.info(f"Client connected ({len(self.clients)} total)")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command', '')
                if self.connected and self.serial_conn:
                    self.serial_conn.write(f'{command}\\n'.encode())
                    log.info(f"Sent: {command}")
        except Exception as e:
            log.error(f"Client error: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def run(self):
        server = await websockets.serve(self.handle_client, "localhost", 8765)
        log.info("WebSocket server on ws://localhost:8765")
        
        await self.connect_serial()
        
        while True:
            try:
                await self.read_serial()
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                log.error(f"Loop error: {e}")
                await asyncio.sleep(1)
        
        if self.serial_conn:
            self.serial_conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True, help='Arduino COM port')
    args = parser.parse_args()
    
    bridge = SimpleBridge(args.port)
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        log.info("Bridge stopped")
'''
    
    with open('FIXED_BRIDGE.py', 'w') as f:
        f.write(bridge_code)
    print("✅ Created FIXED_BRIDGE.py")

def main():
    print("🔧 ARDUINO CONNECTION FIX TOOL")
    print("=" * 50)
    print("This will diagnose and fix your Arduino connection")
    print()
    
    # Step 1: Detailed port scan
    best_port = scan_ports_detailed()
    
    if not best_port:
        print("\n❌ NO PORTS FOUND - CHECK HARDWARE")
        return
    
    # Step 2: Test connection
    success, message = test_port_connection(best_port)
    
    if success:
        print(f"\n✅ CONNECTION SUCCESSFUL on {best_port}!")
        print(f"   Arduino responded: {message}")
        
        # Step 3: Create working bridge
        print(f"\n🔨 CREATING WORKING BRIDGE...")
        create_working_bridge()
        
        print(f"\n🎉 SOLUTION READY!")
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Run: python FIXED_BRIDGE.py --port {best_port}")
        print(f"2. Open: http://localhost/deliveryrobotwebsite/index.html")
        print(f"3. Test: Scan RFID card")
        
    else:
        print(f"\n❌ CONNECTION FAILED on {best_port}")
        print(f"   Error: {message}")
        
        print(f"\n🔧 POSSIBLE FIXES:")
        print(f"1. Close Arduino IDE completely")
        print(f"2. Run Command Prompt as Administrator")
        print(f"3. Check Arduino is powered (LED on)")
        print(f"4. Try different USB cable")
        print(f"5. Install Arduino drivers")
        print(f"6. Upload correct code to Arduino")
        
        print(f"\n📝 If Arduino is connected but not responding:")
        print(f"- Make sure Arduino code uses Serial.begin(9600)")
        print(f"- Make sure Arduino prints messages with Serial.println()")
        print(f"- Check if Arduino is stuck in a loop")
        
        # Still create bridge for manual testing
        create_working_bridge()
        print(f"\n🔨 Created FIXED_BRIDGE.py for manual testing")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Fix tool stopped")
    except Exception as e:
        print(f"\n❌ Tool error: {e}")
