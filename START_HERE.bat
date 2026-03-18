@echo off
echo ========================================
echo    Arduino Bridge Complete Setup
echo ========================================
echo.
echo This will make everything work automatically!
echo.

echo Step 1: Installing packages...
python complete_setup.py
echo.

echo.
echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo Your Arduino bridge is ready!
echo.
echo Next steps:
echo 1. Run: python working_bridge.py --port COM3
echo 2. Open your website
echo 3. Scan RFID card to test
echo.
echo ========================================
pause
