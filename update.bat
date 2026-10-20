@echo off
setlocal enabledelayedexpansion
title PUSTASUB Auto-Updater
cd /d "%~dp0"

echo =======================================================
echo          PUSTASUB BROADCAST SYSTEM UPDATER
echo =======================================================
echo.

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (
    echo Menghentikan instance PUSTASUB yang sedang aktif...
    taskkill /F /PID %%a >nul 2>&1
)

where git >nul 2>&1
if %ERRORLEVEL% equ 0 (
    if exist ".git" (
        echo [Mode: Git Sync] Mengunduh pembaruan dari repository pusat...
        git fetch origin main
        git reset --hard origin/main
        if %ERRORLEVEL% equ 0 (
            echo.
            echo [SUKSES] Sistem PUSTASUB berhasil diperbarui ke versi terbaru!
            goto FINISH
        )
    )
)

echo [Mode: Direct OTA] Mengunduh paket rilis terbaru dari GitHub...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $wc = New-Object System.Net.WebClient; $wc.Headers.Add('User-Agent', 'PUSTASUB-Updater'); $wc.DownloadFile('https://github.com/pusaka-ut/pustasub/archive/refs/heads/main.zip', 'pustasub_update.zip')"

if not exist pustasub_update.zip (
    echo.
    echo [ERROR] Gagal mengunduh berkas update. Pastikan koneksi internet aktif.
    pause
    exit /b 1
)

echo Mengekstrak modul engine dan antarmuka web...
powershell -Command "Expand-Archive -Path 'pustasub_update.zip' -DestinationPath '_temp_update' -Force"

if exist "_temp_update\pustasub-main" (
    xcopy /Y /E /I "_temp_update\pustasub-main\engine" "engine" >nul
    xcopy /Y /E /I "_temp_update\pustasub-main\web" "web" >nul
    if exist "_temp_update\pustasub-main\run.bat" copy /Y "_temp_update\pustasub-main\run.bat" "run.bat" >nul
    if exist "_temp_update\pustasub-main\requirements.txt" copy /Y "_temp_update\pustasub-main\requirements.txt" "requirements.txt" >nul
    rmdir /S /Q "_temp_update"
    del /F /Q "pustasub_update.zip"
    echo.
    echo [SUKSES] Sistem PUSTASUB berhasil diperbarui secara instan!
) else (
    echo.
    echo [ERROR] Format arsip tidak sesuai.
    if exist "_temp_update" rmdir /S /Q "_temp_update"
    if exist "pustasub_update.zip" del /F /Q "pustasub_update.zip"
    pause
    exit /b 1
)

:FINISH
echo.
echo =======================================================
echo Pembaruan telah selesai tanpa merusak data atau model.
echo =======================================================
echo.
set /p START_NOW="Jalankan PUSTASUB sekarang? (Y/N): "
if /i "%START_NOW%"=="Y" (
    start "" run.bat
)
exit /b 0
