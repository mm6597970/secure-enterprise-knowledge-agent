@echo off
setlocal
title Nexora Enterprise RAG - 1-Click Project Launcher
color 0B

echo ========================================================================================
echo                 NEXORA SYSTEMS - ENTERPRISE KNOWLEDGE AGENT (RAG + RBAC)
echo                      1-Click Full-Stack Project Launcher (Windows)
echo ========================================================================================
echo.

:: 1. Start MySQL Docker Container (if available)
echo [1/4] Checking and Starting MySQL Database...
docker compose up -d 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo       [NOTICE] Docker container startup skipped or Docker not active.
    echo       [NOTE] Ensure MySQL 8.0 is running locally on port 3306 (database: nexora_systems).
) else (
    echo       [OK] MySQL Docker container is active and running.
)

echo.
:: 2. Launch AI Service (Python FastAPI on Port 8000)
echo [2/4] Launching AI Knowledge Service (Python FastAPI - Port 8000)...
start "Nexora AI Service [Port 8000]" /D "%~dp0ai-service" cmd /k "title Nexora AI Service [Port 8000] && echo ======================================================= && echo Starting AI Service (FastAPI + LangChain + ChromaDB)... && echo ======================================================= && .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
:: 3. Launch Backend API Gateway (Node.js Express on Port 5000)
echo [3/4] Launching Backend API Gateway (Node.js - Port 5000)...
start "Nexora Backend API [Port 5000]" /D "%~dp0backend" cmd /k "title Nexora Backend API [Port 5000] && echo ======================================================= && echo Starting Backend API Gateway (Express + RBAC + MySQL)... && echo ======================================================= && npm start"

echo.
:: 4. Launch Frontend Dashboard (React + Vite on Port 5173)
echo [4/4] Launching Frontend Dashboard (React + Vite - Port 5173)...
start "Nexora React Frontend [Port 5173]" /D "%~dp0frontend" cmd /k "title Nexora React Frontend [Port 5173] && echo ======================================================= && echo Starting React Web Dashboard... && echo ======================================================= && npm run dev -- --open"

echo.
echo ========================================================================================
echo                         ALL 3 SERVICES LAUNCHED SUCCESSFULLY!
echo ========================================================================================
echo  * Frontend Dashboard  : http://localhost:5173
echo  * Backend API Server  : http://localhost:5000
echo  * Backend Swagger UI  : http://localhost:5000/api-docs
echo  * AI Service API Docs : http://localhost:8000/docs
echo ========================================================================================
echo.
echo DEMO USER ACCOUNTS (RBAC Permissions):
echo  --------------------------------------------------------------------------------------
echo   Role      | Email                              | Password   | Access Privileges
echo  --------------------------------------------------------------------------------------
echo   CEO       | arvind.rajan@nexorasystems.com     | password   | Full access to all data
echo   HR        | divya.iyer@nexorasystems.com       | password   | HR policies, salaries, emp
echo   Employee  | anjali.ramesh@nexorasystems.com    | password   | Employee policies, leave
echo   Intern    | deepa.narayan@nexorasystems.com    | password   | Public company overview
echo  --------------------------------------------------------------------------------------
echo.
echo To STOP all services at any time, run: STOP_PROJECT.bat
echo.
echo Press any key to close this launcher window (services will keep running in their windows)...
pause >nul
