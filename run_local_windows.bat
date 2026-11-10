@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo       UNIVERSE AI STUDIO - LOCAL
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.11 or newer first.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Could not create virtual environment.
    pause
    exit /b 1
  )
)
call ".venv\Scripts\activate.bat"
echo Installing required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo Package installation failed.
  pause
  exit /b 1
)
echo.
echo IMPORTANT: Ollama must be installed and running separately.
echo Open http://127.0.0.1:11434 to verify its local service.
echo Starting UNIVERSE AI STUDIO...
python -m streamlit run app.py
pause
