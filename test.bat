@echo off
REM Paradise Stack - Self-Test Script (Windows)
REM Run this to verify everything works

echo ==========================================
echo Paradise Stack Self-Test
echo ==========================================

REM Test Docker
echo Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo FAIL - Install Docker from https://docker.com
    pause
    exit /b 1
)
echo OK

REM Build
echo Building image (may take a few minutes)...
docker-compose build paradise
if errorlevel 1 (
    echo FAIL - Build failed
    pause
    exit /b 1
)
echo OK

REM Start
echo Starting services...
docker-compose up -d
echo OK - waiting 10 seconds...
timeout /t 10 /nobreak >nul

REM Test health
echo Health check...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:3001/status >nul 2>&1
    if not errorlevel 1 goto :health_ok
    timeout /t 2 /nobreak >nul
)
echo FAIL
docker-compose logs paradise
pause
exit /b 1

:health_ok
echo OK

echo ==========================================
echo All tests passed!
echo ==========================================
echo.
echo Open: http://localhost:3001
echo.
echo Stop: docker-compose down
echo ==========================================
pause
