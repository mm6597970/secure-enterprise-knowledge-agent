@echo off
title Building Nexora Project Launcher .EXE
color 0A

echo ===============================================================================
echo                BUILDING NEXORA PROJECT LAUNCHER (.EXE)
echo ===============================================================================
echo.
echo [1/3] Installing PyInstaller in Python virtual environment...
ai-service\.venv\Scripts\pip.exe install pyinstaller --quiet

echo.
echo [2/3] Compiling Nexora_GUI_Launcher.py into a standalone Windows .EXE...
ai-service\.venv\Scripts\pyinstaller.exe --noconsole --onefile --name "Nexora_Project_Launcher" --clean Nexora_GUI_Launcher.py

echo.
echo [3/3] Moving executable to Project Root...
copy /Y dist\Nexora_Project_Launcher.exe .\Nexora_Project_Launcher.exe >nul
rmdir /S /Q build dist 2>nul
del /Q Nexora_Project_Launcher.spec 2>nul

echo.
echo ===============================================================================
echo  BUILD COMPLETE! You can now run: Nexora_Project_Launcher.exe
echo ===============================================================================
echo.
pause
