@echo off
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo       HELIX TEST AUTOMATION PLATFORM
echo       10-Layer Element Identification
echo ========================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo SUCCESS: Python %PYTHON_VERSION% found

REM Check Docker installation
echo [2/6] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)
for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo SUCCESS: Docker %DOCKER_VERSION% found

REM Check Docker daemon status
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker daemon is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
echo [3/6] Setting up Python environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may have failed to install
    echo Continuing anyway...
)

REM Check for .env file
echo [4/6] Checking environment configuration...
if not exist .env (
    if exist .env.example (
        echo Creating .env file from .env.example
        copy .env.example .env >nul
        echo.
        echo IMPORTANT: Please edit .env file with your configuration
        echo Opening .env file in notepad...
        start notepad .env
        echo.
        echo Press any key when you've updated your .env file...
        pause >nul
    ) else (
        echo WARNING: No .env or .env.example file found
        echo Creating basic .env file...
        (
            echo # Helix Configuration
            echo OPENAI_API_KEY=your-api-key-here
            echo DATABASE_URL=postgresql://helix:helix@localhost:5432/helix
            echo REDIS_URL=redis://localhost:6379
            echo API_PORT=8000
            echo LOG_LEVEL=INFO
        ) > .env
        echo.
        echo IMPORTANT: Please edit .env file with your OpenAI API key
        start notepad .env
        echo.
        echo Press any key when you've updated your .env file...
        pause >nul
    )
)

REM Stop any existing containers
echo [5/6] Preparing Docker services...
echo Stopping any existing containers...
docker-compose down >nul 2>&1

REM Pull latest images
echo Pulling latest Docker images...
docker-compose pull >nul 2>&1

REM Start infrastructure services first
echo Starting infrastructure services...
docker-compose up -d postgres redis >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to start infrastructure services
    echo Checking Docker logs...
    docker-compose logs --tail=20
    pause
    exit /b 1
)

REM Wait for database to be ready
echo Waiting for database to initialize...
set /a count=0
:dbwait
set /a count+=1
if %count% gtr 30 (
    echo ERROR: Database took too long to start
    docker-compose logs postgres
    pause
    exit /b 1
)
docker-compose exec -T postgres pg_isready -U helix >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 1 /nobreak >nul
    goto dbwait
)
echo Database is ready!

REM Initialize database if needed
echo Initializing database schema...
if exist scripts\init_db.sql (
    docker-compose exec -T postgres psql -U helix -d helix -f /docker-entrypoint-initdb.d/init_db.sql >nul 2>&1
)

REM Start all services
echo Starting all Helix services...
docker-compose up -d >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to start services
    docker-compose logs --tail=50
    pause
    exit /b 1
)

REM Wait for API to be ready
echo [6/6] Waiting for API to be ready...
set /a count=0
:apiwait
set /a count+=1
if %count% gtr 60 (
    echo WARNING: API is taking longer than expected to start
    echo Checking logs...
    docker-compose logs api --tail=20
    goto apiready
)
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 1 /nobreak >nul
    goto apiwait
)
:apiready

REM Display success message
cls
echo.
echo ========================================
echo    HELIX STARTED SUCCESSFULLY!
echo ========================================
echo.
echo Service Status:
docker-compose ps
echo.
echo Available Endpoints:
echo   - API:        http://localhost:8000
echo   - API Docs:   http://localhost:8000/docs
echo   - Grafana:    http://localhost:3000 (admin/admin)
echo   - Prometheus: http://localhost:9090
echo.
echo Quick Test Commands:
echo.
echo 1. Test API Health:
echo    curl http://localhost:8000/health
echo.
echo 2. Find Element (Salesforce example):
echo    curl -X POST "http://localhost:8000/find_element" -H "Content-Type: application/json" -d "{\"platform\":\"salesforce_lightning\",\"url\":\"https://example.com\",\"intent\":\"submit button\",\"page_type\":\"form\"}"
echo.
echo 3. View Metrics:
echo    curl http://localhost:8000/metrics
echo.
echo 4. View Logs:
echo    docker-compose logs -f api
echo.
echo 5. Stop Helix:
echo    docker-compose down
echo.
echo Opening API documentation in browser...
timeout /t 3 /nobreak >nul
start http://localhost:8000/docs
echo.
pause