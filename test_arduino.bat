@echo off
echo === Arduino Connection Test ===
echo.
echo This will test your Arduino connection step by step
echo.

echo Step 1: Checking Python...
python -c "import sys; print('Python:', sys.version.split()[0])"
echo.

echo Step 2: Checking packages...
python -c "import serial; import websockets; print('✅ All packages installed')"
echo.

echo Step 3: Scanning ports...
python -c "import serial.tools.list_ports; ports = serial.tools.list_ports.comports(); print('Found', len(ports), 'ports'); [print('  ', p.device, '-', p.description) for p in ports]"
echo.

echo Step 4: Testing connection...
python ultra_test.py
echo.

echo If you see SUCCESS above, run this:
echo python simple_bridge.py --port COM3
echo.
pause
