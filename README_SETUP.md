# Arduino-Website Bridge Setup Guide

## Overview
This guide helps you connect your Arduino RFID system to the delivery robot website using the Python bridge.

## What You Need

### Hardware
- Arduino with RFID scanner (your current setup)
- Computer to run the Python bridge
- USB cable to connect Arduino to computer

### Software
- Python 3.7+ installed
- Required Python packages: `websockets`, `pyserial`

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install websockets pyserial
```

### 2. Update Arduino Code (Optional)
Add these lines to your Arduino code to enable web commands:

```cpp
// Add this after existing includes
#define START_DELIVERY_CMD "START_DELIVERY"
#define EMERGENCY_STOP_CMD "EMERGENCY_STOP"
#define STATUS_CMD "STATUS"

// Add this function to handle serial commands from Python
void checkSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == START_DELIVERY_CMD) {
      // Your existing delivery start logic
      Serial.println("Delivery started via web command");
    }
    else if (command == EMERGENCY_STOP_CMD) {
      // Your existing emergency stop logic
      Serial.println("Emergency stop via web command");
    }
    else if (command == STATUS_CMD) {
      // Send current status
      Serial.print("STATUS:");
      Serial.print(doorOpen ? "DOOR_OPEN" : "DOOR_CLOSED");
      Serial.println();
    }
  }
}

// Add this to your loop() function:
void loop() {
  // ... existing RFID code ...
  
  // Add this check
  checkSerialCommands();
  
  // ... rest of your existing code
}
```

### 3. Configure Serial Port
Check your Arduino's serial port:
- **Windows**: Look in Device Manager for COM port (usually COM3, COM4, etc.)
- **Mac**: `/dev/tty.usbmodemXXXX` or `/dev/cu.usbmodemXXXX`
- **Linux**: `/dev/ttyACM0` or `/dev/ttyUSB0`

Update the port in `arduino_bridge.py`:
```python
# Change this line to match your Arduino's port
arduino_port = 'COM3'  # Windows
# arduino_port = '/dev/ttyACM0'  # Mac/Linux
```

### 4. Start the Bridge Server
```bash
cd c:\xampppp\htdocs\deliveryrobotwebsite
python arduino_bridge.py
```

### 5. Start Your Website
Open your website in a web browser and navigate to the delivery robot page.

## How It Works

### Real-time Updates
1. **RFID Scans**: When you scan an authorized card, the website shows:
   - "Door OPEN" status
   - Success notification with UID
   - Green status light

2. **Web Commands**: Website buttons send commands to Arduino:
   - Start Delivery → Sends "START_DELIVERY" to Arduino
   - Emergency Stop → Sends "EMERGENCY_STOP" to Arduino
   - Refresh Status → Requests current status from Arduino

3. **Connection Status**: 
   - Green light when connected to Arduino
   - Red light when disconnected
   - Auto-reconnect attempts (up to 5 times)

### Features
- **Bidirectional Communication**: Website ↔ Arduino
- **Real-time Status**: Door, robot, battery, connection
- **Notifications**: Success/error messages for all actions
- **Auto-reconnection**: Automatically reconnects if connection lost
- **Multiple Clients**: Multiple browsers can monitor simultaneously

## Troubleshooting

### Common Issues

#### "Arduino not connected"
1. Check USB cable connection
2. Verify correct COM port in bridge.py
3. Close Arduino IDE's Serial Monitor
4. Check if another program is using the port

#### "WebSocket connection failed"
1. Make sure Python bridge is running
2. Check firewall settings
3. Verify port 8765 is not blocked

#### "RFID not detected"
1. Check wiring between RFID reader and Arduino
2. Verify power to RFID module
3. Check authorized UID in Arduino code

### Debug Mode
Enable console logging in your browser to see:
- WebSocket connection status
- Arduino messages received
- Commands sent to Arduino
- Error messages

## Security Notes
- The bridge only accepts connections from localhost
- RFID UIDs are hardcoded in Arduino (secure)
- All commands are logged for debugging

## Next Steps
1. Test basic RFID scanning
2. Test web commands (Start Delivery, Emergency Stop)
3. Verify real-time status updates
4. Test with multiple browser connections

Your delivery robot system is now ready for full web integration!
