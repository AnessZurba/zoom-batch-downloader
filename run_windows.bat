@echo off 

winget list --id Python.Python.3.12 > nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3.12 not found. Installing...
    winget install --id Python.Python.3.12 -e --silent

    for /f "tokens=2*" %%i in ('reg query HKCU\Environment /v PATH ^| find "PATH"') do (
      set PATH=%%j
    )
) else (
    echo Python 3.12 is installed.
)


python -m pip install -r requirements.txt
python zoom_batch_downloader.py

echo.
echo.
pause
