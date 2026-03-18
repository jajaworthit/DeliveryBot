import asyncio
import serial
import websockets
import json

arduino = serial.Serial('COM3', 9600)  # 🔥 CHANGE TO YOUR PORT

clients = set()

async def handler(websocket):
    clients.add(websocket)
    print("Website connected")
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

async def broadcast(message):
    if clients:
        await asyncio.wait(
            [client.send(json.dumps(message)) for client in clients]
        )

async def read_serial():
    while True:
        if arduino.in_waiting:
            line = arduino.readline().decode().strip()
            print("Arduino:", line)

            if line == "DOOR_OPEN":
                await broadcast({"type": "door_status", "status": "OPEN"})
            elif line == "DOOR_CLOSED":
                await broadcast({"type": "door_status", "status": "CLOSED"})
            elif line == "SYSTEM_READY":
                await broadcast({"type": "connection", "status": "CONNECTED"})

        await asyncio.sleep(0.1)

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket Server Started")
    await read_serial()

asyncio.run(main())