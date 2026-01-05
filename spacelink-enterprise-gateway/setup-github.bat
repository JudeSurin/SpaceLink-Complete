@echo off
REM OrbitLink Enterprise Gateway - Automated GitHub Setup Script (Windows)
REM This script will help you quickly push the project to GitHub

echo.
echo ========================================
echo OrbitLink Enterprise Gateway - GitHub Setup
echo ========================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed. Please install git first.
    echo Visit: https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Get GitHub username
set /p GITHUB_USERNAME="Enter your GitHub username: "

if "%GITHUB_USERNAME%"=="" (
    echo ERROR: GitHub username is required
    pause
    exit /b 1
)

REM Repository name
set REPO_NAME=orbitlink-enterprise-gateway

echo.
echo Configuration:
echo   GitHub Username: %GITHUB_USERNAME%
echo   Repository Name: %REPO_NAME%
echo   Repository URL: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.

set /p CONFIRM="Does this look correct? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Setup cancelled
    pause
    exit /b 1
)

echo.
echo Setting up Git repository...

REM Initialize git if not already done
if not exist ".git" (
    git init
    echo Git repository initialized
) else (
    echo Git repository already exists
)

REM Add all files
echo Staging files...
git add .

REM Commit
echo Creating initial commit...
git commit -m "feat: Initial release of OrbitLink Enterprise Gateway - Enterprise API gateway with FastAPI - Dual authentication (API keys + OAuth2/JWT) - RBAC with multi-tenant isolation - Telemetry ingestion and network monitoring - Partner onboarding workflows - Python SDK and comprehensive documentation - Docker deployment support"

REM Set main branch
git branch -M main

REM Add remote
set REMOTE_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
git remote | findstr "origin" >nul
if %ERRORLEVEL% EQU 0 (
    echo Remote 'origin' already exists, updating...
    git remote set-url origin %REMOTE_URL%
) else (
    echo Adding remote repository...
    git remote add origin %REMOTE_URL%
)

echo.
echo ========================================
echo IMPORTANT: Create GitHub Repository First!
echo ========================================
echo.
echo Before pushing, you need to create the repository on GitHub:
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: %REPO_NAME%
echo 3. Description: Enterprise satellite connectivity integration platform
echo 4. Choose: Public (recommended for portfolio)
echo 5. DO NOT initialize with README, .gitignore, or license
echo 6. Click 'Create repository'
echo.
pause

echo.
echo Pushing to GitHub...
echo.

REM Push to GitHub
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Project pushed to GitHub!
    echo ========================================
    echo.
    echo Your repository: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
    echo Next steps:
    echo 1. View your repo: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo 2. Add repository description and topics on GitHub
    echo 3. Create a release (v1.0.0^)
    echo 4. Test locally: docker-compose up
    echo 5. Add to your resume and LinkedIn!
    echo.
    echo Ready for interviews!
) else (
    echo.
    echo ========================================
    echo Push Failed
    echo ========================================
    echo.
    echo Common issues:
    echo.
    echo 1. Authentication Required:
    echo    - Use GitHub CLI: gh auth login
    echo    - Or create Personal Access Token:
    echo      https://github.com/settings/tokens
    echo.
    echo 2. Repository doesn't exist:
    echo    - Make sure you created it at: https://github.com/new
    echo    - Repository name must be: %REPO_NAME%
    echo.
    echo 3. Try manual push:
    echo    git push -u origin main
)

echo.
echo For detailed instructions, see: GITHUB_SETUP_GUIDE.md
echo.
pause
