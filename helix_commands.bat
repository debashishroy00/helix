@echo off
REM ==============================================================================
REM Helix Command Dispatcher
REM Usage: helix [command]
REM ==============================================================================

if "%1"=="" goto start
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="test" goto test
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="shell" goto shell
if "%1"=="clean" goto clean
if "%1"=="help" goto help

echo Unknown command: %1
goto help

:start
call helix.bat
goto end

:stop
echo Stopping Helix services...
docker-compose -f docker-compose.dev.yml down
echo Services stopped.
goto end

:test
echo Running Helix tests...
python test_10_layers.py
echo.
echo Run test_browsers.py for browser tests
goto end

:logs
echo Showing Helix logs (Ctrl+C to stop)...
docker-compose -f docker-compose.dev.yml logs -f helix-api
goto end

:status
echo Checking Helix status...
curl -s http://localhost:8000/test/system_status | python -m json.tool
goto end

:shell
echo Entering Helix API container...
docker-compose -f docker-compose.dev.yml exec helix-api bash
goto end

:clean
call cleanup.bat
goto end

:help
echo.
echo Helix Commands:
echo   helix         - Start Helix platform
echo   helix stop    - Stop all services
echo   helix test    - Run system tests
echo   helix logs    - View live logs
echo   helix status  - Check system status
echo   helix shell   - Enter API container
echo   helix clean   - Clean up for GitHub
echo   helix help    - Show this help
echo.

:end