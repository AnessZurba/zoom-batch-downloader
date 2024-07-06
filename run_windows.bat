@echo off 

winget --version > nul 2>&1
if %errorlevel% neq 0 (
    echo winget is not installed on this system.
    echo winget is standard Windows application starting from Windows 10 1709.
    echo The script will now try to install winget. This requires Administrator privilages.
    echo You might be asked to rerun this script as an Administrator for this to work.
    echo.
    pause
    echo.
    
    powershell -command "irm winget.pro | iex"
    if %errorlevel% neq 0 (
        echo.
        echo.
        pause 
        exit /b 1
    )

    set "PATH=C:\Windows\System32;%PATH%"
    for /f "tokens=2*" %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH ^| find "PATH"') do call set systemPATH=%%j
    for /f "tokens=2*" %%i in ('reg query "HKCU\Environment" /v PATH ^| find "PATH"') do call set PATH=%systemPATH%;%%j
)

winget list --id Python.Python.3.12 -e --accept-source-agreements > nul 2>&1 
if %errorlevel% neq 0 (
    echo Python 3.12 not found. Installing...
    winget install --id Python.Python.3.12 -e --silent

    set "PATH=C:\Windows\System32;%PATH%"
    for /f "tokens=2*" %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH ^| find "PATH"') do call set systemPATH=%%j
    for /f "tokens=2*" %%i in ('reg query "HKCU\Environment" /v PATH ^| find "PATH"') do call set PATH=%systemPATH%;%%j
) else (
    echo Python 3.12 is installed.
)


python -m pip install -r requirements.txt
python zoom_batch_downloader.py

echo.
echo.
pause
