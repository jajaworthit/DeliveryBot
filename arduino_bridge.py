#!/usr/bin/env python3
"""
Arduino <-> WebSocket Bridge for Delivery Robot
------------------------------------------------
Fixes:
  - websockets >= 10 compatibility (no more 'path' argument crash)
  - Correct RFID parsing (UID and ACCESS on separate lines)
  - Bidirectional: browser can send commands to Arduino
  - Auto-reconnect when Arduino unplugs
  - Clean shutdown on Ctrl+C

Requirements:
  pip install pyserial websockets

Usage:
  python arduino_bridge.py
  python arduino_bridge.py --port COM3
  python arduino_bridge.py --port /dev/ttyACM0 --ws-port 8765
"""

import asyncio
import json
import logging
import re
import serial
import serial.tools.list_ports
import websockets
import argparse
from datetime import datetime
from typing import Optional

# ── CONFIG (edit these if you don't want to use CLI args) ───────────────────
DEFAULT_PORT    = None        # None = auto-detect
DEFAULT_BAUD    = 9600
DEFAULT_HOST    = "localhost"
DEFAULT_WS_PORT = 8765
RECONNECT_DELAY = 3           # seconds between reconnect attempts
# ────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# ── Shared state ─────────────────────────────────────────────────────────────
state = {
    "door":        "CLOSED",
    "robot":       "IDLE",
    "connected":   False,
    "last_uid":    None,
    "last_scan":   None,
    "pending_uid": None,   # UID seen but no access verdict yet
}

clients: set = set()       # connected browser WebSocket clients
serial_conn: Optional[serial.Serial] = None

# ── Helpers ──────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now().isoformat()

async def broadcast(msg: dict):
    """Send JSON to every connected browser client."""
    if not clients:
        return
    payload = json.dumps(msg)
    dead = set()
    for ws in clients:
        try:
            await ws.send(payload)
        except Exception:
            dead.add(ws)
    clients.difference_update(dead)

def detect_port() -> Optional[str]:
    """Auto-detect first Arduino-looking serial port."""
    keywords = ["arduino", "ch340", "cp210", "ftdi", "usb serial", "uart"]
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        if any(k in desc for k in keywords):
            log.info(f"Auto-detected: {p.device}  ({p.description})")
            return p.device
    all_ports = serial.tools.list_ports.comports()
    if all_ports:
        log.warning(f"No Arduino found — using first port: {all_ports[0].device}")
        return all_ports[0].device
    return None

# ── Arduino serial parser ────────────────────────────────────────────────────

async def parse_line(line: str):
    """
    Parse one line from Arduino Serial.println() and broadcast to browser.

    Your sketch prints UID on one line, then ACCESS GRANTED/DENIED on the next,
    so we buffer the UID in state['pending_uid'] until the verdict arrives.
    """
    line = line.strip()
    if not line:
        return

    log.info(f"Arduino → {line}")
    low = line.lower()

    # ── UID line (e.g. "Scanned UID: 0xC3 0x33 0xA8 0x39") ──────────────
    if low.startswith("scanned uid:"):
        hex_bytes = re.findall(r"0x([0-9a-fA-F]+)", line, re.IGNORECASE)
        uid = ":".join(h.upper() for h in hex_bytes) if hex_bytes else "UNKNOWN"
        state["pending_uid"] = uid
        state["last_uid"]    = uid
        state["last_scan"]   = now_iso()
        # Don't broadcast yet — wait for ACCESS verdict on next line

    # ── Access granted ────────────────────────────────────────────────────
    elif "access granted" in low:
        await broadcast({
            "type":        "rfid_scan",
            "access":      "GRANTED",
            "uid":         state["pending_uid"] or state["last_uid"] or "UNKNOWN",
            "door_status": state["door"],
            "timestamp":   now_iso(),
        })
        state["pending_uid"] = None

    # ── Access denied ─────────────────────────────────────────────────────
    elif "access denied" in low:
        await broadcast({
            "type":        "rfid_scan",
            "access":      "DENIED",
            "uid":         state["pending_uid"] or state["last_uid"] or "UNKNOWN",
            "door_status": state["door"],
            "timestamp":   now_iso(),
        })
        state["pending_uid"] = None

    # ── Door OPEN ─────────────────────────────────────────────────────────
    elif "door open" in low:
        state["door"] = "OPEN"
        await broadcast({"type": "door_status", "status": "OPEN", "timestamp": now_iso()})

    # ── Door CLOSED ───────────────────────────────────────────────────────
    elif "door closed" in low or "door close" in low:
        state["door"] = "CLOSED"
        await broadcast({"type": "door_status", "status": "CLOSED", "timestamp": now_iso()})

    # ── Ready ─────────────────────────────────────────────────────────────
    elif "ready" in low and "scan" in low:
        await broadcast({
            "type":      "system_status",
            "status":    "READY",
            "message":   line,
            "timestamp": now_iso(),
        })

    # ── Generic passthrough ───────────────────────────────────────────────
    else:
        await broadcast({
            "type":      "system_status",
            "status":    "INFO",
            "message":   line,
            "timestamp": now_iso(),
        })

# ── Serial loop (with auto-reconnect) ────────────────────────────────────────

async def serial_loop(port: str, baud: int):
    """Keeps trying to (re)connect to Arduino every RECONNECT_DELAY seconds."""
    global serial_conn

    while True:
        try:
            log.info(f"Connecting to Arduino on {port} @ {baud} baud …")
            serial_conn = serial.Serial(port=port, baudrate=baud, timeout=1)
            state["connected"] = True

            await broadcast({
                "type":    "connection",
                "status":  "CONNECTED",
                "message": f"Arduino connected on {port}",
            })
            log.info("✅ Arduino connected")

            # Read loop
            while True:
                await asyncio.sleep(0.05)
                try:
                    if serial_conn.in_waiting:
                        raw  = serial_conn.readline()
                        line = raw.decode("utf-8", errors="ignore")
                        await parse_line(line)
                except serial.SerialException as e:
                    log.error(f"Read error: {e}")
                    break

        except serial.SerialException as e:
            log.error(f"Could not open {port}: {e}")
        except Exception as e:
            log.error(f"Serial loop error: {e}")
        finally:
            if serial_conn and serial_conn.is_open:
                serial_conn.close()
            state["connected"] = False
            serial_conn = None
            log.warning(f"Arduino disconnected — retrying in {RECONNECT_DELAY}s …")
            await broadcast({
                "type":    "connection",
                "status":  "DISCONNECTED",
                "message": "Arduino disconnected — reconnecting …",
            })
            await asyncio.sleep(RECONNECT_DELAY)

# ── Send command to Arduino ───────────────────────────────────────────────────

def send_to_arduino(command: str) -> bool:
    """Write a newline-terminated command to Arduino over serial."""
    if serial_conn and serial_conn.is_open:
        try:
            serial_conn.write((command + "\n").encode())
            log.info(f"Browser → Arduino: {command}")
            return True
        except serial.SerialException as e:
            log.error(f"Write error: {e}")
    else:
        log.warning("Cannot send — Arduino not connected")
    return False

# ── WebSocket handler ─────────────────────────────────────────────────────────

# Map browser command strings → Arduino command strings
COMMAND_MAP = {
    "delivery":        "START_DELIVERY",
    "start_delivery":  "START_DELIVERY",
    "emergency":       "EMERGENCY_STOP",
    "emergency_stop":  "EMERGENCY_STOP",
    "stop":            "EMERGENCY_STOP",
    "refresh_status":  "STATUS",
    "status":          "STATUS",
}

async def ws_handler(websocket):
    """
    Handle one browser WebSocket connection.
    Compatible with websockets >= 10 (handler takes only websocket, no path).
    """
    clients.add(websocket)
    log.info(f"Browser connected  ({len(clients)} total)")

    # Send current state immediately on connect
    await websocket.send(json.dumps({
        "type":              "initial_status",
        "arduino_connected": state["connected"],
        "door_status":       state["door"],
        "robot_status":      state["robot"],
        "last_uid":          state["last_uid"],
        "last_scan":         state["last_scan"],
        "timestamp":         now_iso(),
    }))

    try:
        async for raw in websocket:
            try:
                data        = json.loads(raw)
                command     = data.get("command", "").lower()
                arduino_cmd = COMMAND_MAP.get(command)

                if arduino_cmd:
                    ok = send_to_arduino(arduino_cmd)
                    await websocket.send(json.dumps({
                        "type":    "command_ack",
                        "command": arduino_cmd,
                        "sent":    ok,
                        "timestamp": now_iso(),
                    }))
                else:
                    log.warning(f"Unknown command from browser: {command!r}")

            except json.JSONDecodeError:
                log.warning(f"Bad JSON from browser: {raw}")

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.discard(websocket)
        log.info(f"Browser disconnected  ({len(clients)} remaining)")

# ── Main ──────────────────────────────────────────────────────────────────────

async def main(port: str, baud: int, host: str, ws_port: int):
    # Start serial read/reconnect loop in background
    asyncio.create_task(serial_loop(port, baud))

    # Start WebSocket server
    # websockets >= 10: serve() accepts a single-argument handler (no path)
    async with websockets.serve(ws_handler, host, ws_port):
        log.info(f"🌐 WebSocket → ws://{host}:{ws_port}")
        log.info(f"🔌 Serial port → {port}  ({baud} baud)")
        log.info("🤖 Bridge running — open your HTML file in a browser")
        log.info("   Ctrl+C to stop\n")
        await asyncio.Future()   # run forever


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arduino ↔ Website Bridge — Delivery Robot")
    parser.add_argument("--port",    default=DEFAULT_PORT,    help="Arduino COM port (auto-detect if omitted)")
    parser.add_argument("--baud",    default=DEFAULT_BAUD,    type=int,  help="Baud rate (default 9600)")
    parser.add_argument("--host",    default=DEFAULT_HOST,               help="WebSocket host (default localhost)")
    parser.add_argument("--ws-port", default=DEFAULT_WS_PORT, type=int,  help="WebSocket port (default 8765)", dest="ws_port")
    args = parser.parse_args()

    port = args.port or detect_port()
    if not port:
        print("❌  No serial port found. Plug in your Arduino or run with --port COM3")
        raise SystemExit(1)

    print("=" * 54)
    print("  Arduino ↔ Website Bridge  |  Delivery Robot System")
    print("=" * 54)

    try:
        asyncio.run(main(port, args.baud, args.host, args.ws_port))
    except KeyboardInterrupt:
        print("\n🛑  Bridge stopped.")
