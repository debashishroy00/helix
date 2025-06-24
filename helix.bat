@echo off
REM ==============================================================================
REM Helix: Agentic RAG Test Automation Platform
REM Patent-Pending 10-Layer Element Identification System
REM GitHub: https://github.com/debashishroy00/helix
REM ==============================================================================

echo.
echo  HELIX - AI Test Automation Platform
echo  ===================================
echo  10-Layer Patent-Pending System
echo.

REM Check for Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/
    pause
    exit /b 1
)

REM Check Docker daemon
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker daemon is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo ERROR: .env file not found!
    if exist .env.example (
        echo Creating .env from template...
        copy .env.example .env
        echo.
        echo IMPORTANT: Edit .env and add your OpenAI API key
        echo   OPENAI_API_KEY=your-actual-key-here
        notepad .env
    )
    pause
    exit /b 1
)

echo [1/5] Stopping any existing containers...
docker-compose -f docker-compose.dev.yml down 2>nul

echo [2/5] Starting PostgreSQL and Redis...
docker-compose -f docker-compose.dev.yml up -d postgres redis

echo [3/5] Waiting for database (10 seconds)...
timeout /t 10 /nobreak > nul

echo [4/5] Starting Helix API server...
docker-compose -f docker-compose.dev.yml up -d helix-api

echo [5/5] Waiting for API startup (20 seconds)...
timeout /t 20 /nobreak > nul

echo.
echo ===============================================
echo HELIX IS READY!
echo ===============================================
echo.
echo Service URLs:
echo   - API:        http://localhost:8000
echo   - API Docs:   http://localhost:8000/docs
echo   - PostgreSQL: localhost:5433
echo   - Redis:      localhost:6380
echo.

REM Test API health
curl -s http://localhost:8000/ > nul 2>&1
if %errorlevel% equ 0 (
    echo Status: API HEALTHY - Layer 1 (Semantic) OPERATIONAL
) else (
    echo Status: API starting... wait 30s or check logs
)

echo.
echo Quick Commands:
echo   helix test      - Run system tests
echo   helix logs      - View live logs
echo   helix stop      - Stop all services
echo   helix status    - Check system status
echo   helix shell     - Enter API container
echo.
echo Press any key to view logs (Ctrl+C to stop)...
pause > nul

docker-compose -f docker-compose.dev.yml logs -f helix-api