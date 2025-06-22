@echo off
echo.
echo ========================================
echo       HELIX Quick Commit Tool
echo ========================================
echo.

:: Check if we're in the right directory
if not exist ".git" (
    echo ERROR: Not in a git repository!
    echo Make sure you run this from the HELIX project root.
    pause
    exit /b 1
)

:: Show current status
echo Current Status:
echo ---------------
git status --short
echo.

:: Check if there are changes to commit
git diff --quiet --exit-code
if %errorlevel% == 0 (
    git diff --cached --quiet --exit-code
    if %errorlevel% == 0 (
        echo No changes to commit!
        echo.
        pause
        exit /b 0
    )
)

:: Ask for commit message
echo Enter commit message (or press Enter for default):
set /p commit_message="Message: "

:: Use default message if none provided
if "%commit_message%"=="" (
    set commit_message=Update: %date% %time%
)

:: Add all changes
echo.
echo Adding all changes...
git add .

:: Commit changes
echo.
echo Committing changes...
git commit -m "%commit_message%"

:: Push to GitHub
echo.
echo Pushing to GitHub...
git push origin main

:: Show result
echo.
if %errorlevel% == 0 (
    echo ========================================
    echo    SUCCESS! Changes pushed to GitHub
    echo ========================================
) else (
    echo ========================================
    echo    ERROR! Push failed. Check details above.
    echo ========================================
)

echo.
pause