#!/usr/bin/env python3
"""
Complete Arduino Bridge Setup
One-click solution for Arduino-website integration
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages"""
    print("🔧 Installing required packages...")
    
    try:
        # Install pyserial and websockets
        subprocess.run([sys.executable, "-m", "pip", "install", "pyserial", "websockets"], 
                     check=True, capture_output=True, text=True)
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation failed: {e}")
        return False

def test_connection():
    """Test Arduino connection"""
    print("\n🔍 Testing Arduino connection...")
    
    try:
        import serial
        import serial.tools.list_ports
        
        # List ports
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("❌ No serial ports found!")
            print("   - Check Arduino USB connection")
            print("   - Install Arduino drivers")
            return None, False
        
        print(f"📡 Found {len(ports)} ports:")
        arduino_port = None
        
        for i, port in enumerate(ports, 1):
            print(f"   {i}. {port.device} - {port.description}")
            
            # Look for Arduino
            desc_lower = port.description.lower()
            if 'arduino' in desc_lower or 'ch340' in desc_lower or 'cp210' in desc_lower:
                arduino_port = port.device
                print(f"   🎯 Arduino detected!")
        
        # If no Arduino found, use first port
        if not arduino_port and ports:
            arduino_port = ports[0].device
            print(f"   ⚠️ Using first available port: {arduino_port}")
        
        # Test the port
        if arduino_port:
            try:
                ser = serial.Serial(arduino_port, 9600, timeout=3)
                print(f"✅ Successfully connected to {arduino_port}!")
                ser.close()
                return arduino_port, True
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return arduino_port, False
        
        return None, False
        
    except ImportError:
        print("❌ pyserial not installed!")
        return None, False

def create_simple_bridge():
    """Create a simple working bridge"""
    simple_bridge_code = '''#!/usr/bin/env python3
"""
Working Arduino Bridge - Simplified Version
"""

import serial
import json
import asyncio
import websockets
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkingBridge:
    def __init__(self, port):
        self.port = port
        self.serial_conn = None
        self.clients = set()
        self.connected = False
        
    async def connect_serial(self):
        """Connect to Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, 9600, timeout=2)
            await asyncio.sleep(2)
            self.connected = True
            logger.info(f"✅ Connected to Arduino on {self.port}")
            await self.broadcast({'type': 'connection', 'status': 'CONNECTED'})
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.connected = False
            await self.broadcast({'type': 'connection', 'status': 'DISCONNECTED'})
            return False
    
    async def read_serial(self):
        """Read from Arduino"""
        if not self.connected:
            return
        
        try:
            if self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    logger.info(f"Arduino: {line}")
                    await self.process_line(line)
        except Exception as e:
            logger.error(f"Read error: {e}")
    
    async def process_line(self, line):
        """Process Arduino data"""
        line_lower = line.lower()
        
        if 'door open' in line_lower:
            await self.broadcast({'type': 'door_status', 'status': 'OPEN'})
        elif 'door close' in line_lower or 'door closed' in line_lower:
            await self.broadcast({'type': 'door_status', 'status': 'CLOSED'})
        elif 'access granted' in line_lower:
            await self.broadcast({'type': 'rfid_scan', 'access': 'GRANTED', 'message': line})
        elif 'access denied' in line_lower:
            await self.broadcast({'type': 'rfid_scan', 'access': 'DENIED', 'message': line})
    
    async def broadcast(self, data):
        """Send to web clients"""
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
        """Handle web client"""
        self.clients.add(websocket)
        logger.info(f"Client connected (total: {len(self.clients)})")
        
        await websocket.send(json.dumps({
            'type': 'initial_status',
            'connected': self.connected,
            'port': self.port
        }))
        
        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command', '')
                if self.connected and self.serial_conn:
                    self.serial_conn.write(f'{command}\\n'.encode())
                    logger.info(f"Sent to Arduino: {command}")
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def run(self):
        """Main loop"""
        server = await websockets.serve(self.handle_client, "localhost", 8765)
        logger.info("WebSocket server on ws://localhost:8765")
        
        await self.connect_serial()
        
        while True:
            try:
                await self.read_serial()
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")
                await asyncio.sleep(1)
        
        if self.serial_conn:
            self.serial_conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True, help='Arduino COM port')
    args = parser.parse_args()
    
    bridge = WorkingBridge(args.port)
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        logger.info("Bridge stopped")
'''
    
    with open('working_bridge.py', 'w') as f:
        f.write(simple_bridge_code)
    
    print("✅ Created working_bridge.py")
    return True

def main():
    """Main setup process"""
    print("=== Complete Arduino Bridge Setup ===")
    print("This will make everything work in one go!")
    print()
    
    # Step 1: Install packages
    if not install_packages():
        print("❌ Failed to install packages")
        return
    
    # Step 2: Test connection
    port, success = test_connection()
    
    if not port:
        print("❌ No Arduino found!")
        print("\nTroubleshooting:")
        print("1. Check Arduino USB connection")
        print("2. Install Arduino drivers")
        print("3. Try different USB port")
        return
    
    if not success:
        print(f"⚠️ Arduino found on {port} but connection failed")
        print("Try running as Administrator")
    
    # Step 3: Create working bridge
    if not create_simple_bridge():
        print("❌ Failed to create bridge")
        return
    
    # Step 4: Instructions
    print(f"\n🎉 SETUP COMPLETE!")
    print(f"\n🚀 To start the bridge:")
    print(f"   python working_bridge.py --port {port}")
    print(f"\n🌐 Then open your website and it will connect automatically!")
    print(f"\n📋 Final checklist:")
    print(f"   [x] Python packages installed")
    print(f"   [x] Arduino port found: {port}")
    print(f"   [x] Bridge script created")
    print(f"   [ ] Start bridge with command above")
    print(f"   [ ] Open website")
    print(f"   [ ] Test RFID scanning")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup stopped")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
