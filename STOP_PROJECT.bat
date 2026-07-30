@echo off
setlocal
title Nexora Enterprise RAG - Service Shutdown
color 0C

echo ========================================================================================
echo                         STOPPING NEXORA ENTERPRISE RAG SERVICES
echo ========================================================================================
echo.

echo [1/4] Terminating Python AI Service (Port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a 2>nul
)

echo.
echo [2/4] Terminating Node.js Backend API (Port 5000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a 2>nul
)

echo.
echo [3/4] Terminating Vite React Frontend (Port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /f /pid %%a 2>nul
)

echo.
echo [4/4] Cleaning up any remaining Node.js or Uvicorn background instances...
taskkill /f /im node.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul

echo.
echo ========================================================================================
echo                       ALL NEXORA SERVICES HAVE BEEN SHUT DOWN.
echo ========================================================================================
echo.
echo Press any key to exit...
pause >nul
