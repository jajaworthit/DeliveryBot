@echo off
cls
echo ========================================
echo    DELIVERY ROBOT SYSTEM - ALIGNED
echo ========================================
echo.
echo 🚀 Starting aligned system...
echo.

echo Step 1: Installing packages...
python -m pip install pyserial websockets
echo.

echo Step 2: Starting Arduino bridge...
echo.
echo 📡 Bridge will auto-detect Arduino port...
echo 🌐 WebSocket server on ws://localhost:8765
echo.
python arduino_bridge.py
echo.

echo ========================================
echo    READY!
echo ========================================
echo.
echo 🌐 Website: http://localhost/deliveryrobotwebsite/index.html
echo 🔌 Bridge: Running on ws://localhost:8765
echo.
echo 📋 What to do:
echo    1. Open website in browser
echo    2. Scan RFID card on Arduino
echo    3. Watch real-time updates
echo.
echo ========================================
pause
