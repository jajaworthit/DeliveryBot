@echo off
cls
echo ========================================
echo    ARDUINO CONNECTION FIX TOOL
echo ========================================
echo.
echo 🔧 This will diagnose and fix Arduino connection
echo.

python ARDUINO_FIX.py
echo.

echo ========================================
echo    FIX COMPLETE!
echo ========================================
echo.
echo 📋 The tool created FIXED_BRIDGE.py
echo 📋 Follow the instructions shown above
echo.
echo If connection still fails:
echo    1. Close Arduino IDE completely
echo    2. Run this batch as Administrator
echo    3. Check Arduino USB cable
echo    4. Make sure Arduino LED is ON
echo.
pause
