#!/usr/bin/env python3
"""
Simple Arduino Bridge - Minimal Version
Easier to debug Arduino connection issues
"""

import serial
import json
import asyncio
import websockets
import logging
from datetime import datetime

# Simple logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleArduinoBridge:
    def __init__(self, port=None):
        self.port = port
        self.serial_conn = None
        self.clients = set()
        self.connected = False
        
    async def connect_serial(self):
        """Simple serial connection"""
        if not self.port:
            # Auto-detect port
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            
            logger.info("🔍 Scanning for Arduino...")
            for p in ports:
                logger.info(f"  Found: {p.device} - {p.description}")
                if 'arduino' in p.description.lower() or 'ch340' in p.description.lower():
                    self.port = p.device
                    logger.info(f"🎯 Using Arduino port: {self.port}")
                    break
            
            if not self.port and ports:
                self.port = ports[0].device
                logger.warning(f"⚠️ Using first port: {self.port}")
        
        if not self.port:
            logger.error("❌ No serial port found!")
            return False
        
        try:
            logger.info(f"🔌 Connecting to {self.port}...")
            
            # Close existing connection
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            
            # Open new connection
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=9600,
                timeout=2,
                write_timeout=2
            )
            
            # Wait for Arduino
            await asyncio.sleep(3)
            
            # Test connection
            self.serial_conn.write(b'Hello\n')
            await asyncio.sleep(1)
            
            self.connected = True
            logger.info(f"✅ Connected to Arduino on {self.port}")
            
            # Notify web clients
            await self.broadcast({
                'type': 'connection',
                'status': 'CONNECTED',
                'message': f'Arduino connected on {self.port}'
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.connected = False
            
            # Notify web clients
            await self.broadcast({
                'type': 'connection', 
                'status': 'DISCONNECTED',
                'message': f'Failed: {str(e)}'
            })
            return False
    
    async def read_serial(self):
        """Read data from Arduino"""
        if not self.connected or not self.serial_conn:
            return
        
        try:
            if self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    logger.info(f"📨 Arduino: {line}")
                    await self.process_line(line)
        except Exception as e:
            logger.error(f"❌ Read error: {e}")
            self.connected = False
    
    async def process_line(self, line):
        """Process Arduino data"""
        line_lower = line.lower()
        
        if 'door open' in line_lower:
            await self.broadcast({
                'type': 'door_status',
                'status': 'OPEN',
                'timestamp': datetime.now().isoformat()
            })
        elif 'door close' in line_lower:
            await self.broadcast({
                'type': 'door_status', 
                'status': 'CLOSED',
                'timestamp': datetime.now().isoformat()
            })
        elif 'access granted' in line_lower:
            await self.broadcast({
                'type': 'rfid_scan',
                'access': 'GRANTED',
                'message': line,
                'timestamp': datetime.now().isoformat()
            })
        elif 'access denied' in line_lower:
            await self.broadcast({
                'type': 'rfid_scan',
                'access': 'DENIED', 
                'message': line,
                'timestamp': datetime.now().isoformat()
            })
    
    async def broadcast(self, data):
        """Send to all web clients"""
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
        logger.info(f"🌐 Client connected (total: {len(self.clients)})")
        
        # Send current status
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
                    self.serial_conn.write(f'{command}\n'.encode())
                    logger.info(f"📤 Sent to Arduino: {command}")
                else:
                    logger.warning(f"⚠️ Can't send command - not connected")
                    
        except Exception as e:
            logger.error(f"❌ Client error: {e}")
        finally:
            self.clients.discard(websocket)
            logger.info(f"🌐 Client disconnected (total: {len(self.clients)})")
    
    async def run(self):
        """Main loop"""
        # Start WebSocket server
        server = await websockets.serve(self.handle_client, "localhost", 8765)
        logger.info("🌐 WebSocket server on ws://localhost:8765")
        
        # Try to connect to Arduino
        await self.connect_serial()
        
        # Main loop
        while True:
            try:
                await self.read_serial()
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                logger.info("🛑 Stopping...")
                break
            except Exception as e:
                logger.error(f"❌ Loop error: {e}")
                await asyncio.sleep(1)
        
        # Cleanup
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()

if __name__ == "__main__":
    print("=== Simple Arduino Bridge ===")
    print("Easier debugging version")
    print()
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Arduino COM port')
    args = parser.parse_args()
    
    bridge = SimpleArduinoBridge(args.port)
    
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print("\n👋 Bridge stopped")
