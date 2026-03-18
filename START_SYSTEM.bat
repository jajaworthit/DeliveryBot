@echo off
cls
echo ========================================
echo    DELIVERY ROBOT SYSTEM
echo ========================================
echo.
echo 🚀 Starting complete setup...
echo.

echo Step 1: Installing packages...
python complete_setup.py
echo.

echo Step 2: Starting Arduino bridge...
echo.
echo 📡 Looking for Arduino...
python working_bridge.py --port COM3
echo.
echo ========================================
echo    SYSTEM READY!
echo ========================================
echo.
echo 🌐 Website: http://localhost/deliveryrobotwebsite/index.html
echo 🔌 Bridge: Running on ws://localhost:8765
echo.
echo 📋 What to do next:
echo    1. Open the website in your browser
echo    2. Scan your RFID card on Arduino
echo    3. Watch real-time status updates
echo    4. Test Start Delivery button
echo.
echo ========================================
echo Press Ctrl+C to stop the bridge
echo ========================================
pause
