@echo off
cls
echo ========================================
echo    ARDUINO CONNECTION FIX - AUTO RUN
echo ========================================
echo.

echo 🔧 Fixing directory issue...
cd /d c:\xampppp\htdocs\deliveryrobotwebsite
echo ✅ Changed to project directory

echo.
echo 🔍 Running Arduino fix tool...
python ARDUINO_FIX.py
echo.

echo ========================================
echo    FIX COMPLETE!
echo ========================================
echo.

echo 📋 The tool created FIXED_BRIDGE.py in this folder
echo 📋 Now running the fixed bridge...
echo.

if exist FIXED_BRIDGE.py (
    echo 🚀 Starting FIXED_BRIDGE...
    python FIXED_BRIDGE.py --port COM3
) else (
    echo ❌ FIXED_BRIDGE.py not found
    echo    Run the fix tool first
)

echo.
echo ========================================
pause
