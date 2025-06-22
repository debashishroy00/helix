@echo off
REM ==============================================================================
REM Helix Cleanup Script - Prepare for GitHub
REM ==============================================================================

echo.
echo Cleaning up Helix project for GitHub...
echo ======================================
echo.

REM Stop all containers
echo [1/5] Stopping Docker containers...
docker-compose -f docker-compose.dev.yml down 2>nul

REM Remove Python cache
echo [2/5] Removing Python cache...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM Remove test artifacts
echo [3/5] Removing test artifacts...
if exist .pytest_cache rd /s /q .pytest_cache
if exist .coverage del .coverage
if exist htmlcov rd /s /q htmlcov

REM Remove virtual environment
echo [4/5] Removing virtual environment...
if exist venv rd /s /q venv

REM Clean Docker volumes (optional)
echo [5/5] Docker cleanup...
docker system prune -f 2>nul

echo.
echo Cleanup complete!
echo.
echo Files to check before committing:
echo   - .env (should NOT be committed - contains API keys)
echo   - Any test_*.py files (decide which to keep)
echo   - Old batch files (consolidate into helix.bat)
echo.
pause