@echo off
REM =============================================================
REM CuPy用 一時フォルダ・実行用バッチ（_internal含む）
REM =============================================================

set "TEMP=C:\cupy_temp"
set "TMP=C:\cupy_temp"
set "WORKDIR=C:\cupy_run"
set "SRC_DIR=C:\Users\タケックス㈱ 設計課\Desktop\benchmark_test"
set "LOGFILE=%WORKDIR%\move_log.txt"

REM --- 一時フォルダ作成 ---
if not exist "%TEMP%" mkdir "%TEMP%"
if not exist "%WORKDIR%" mkdir "%WORKDIR%"

REM --- フォルダ丸ごと移動（robocopy） ---
echo =============================================================
echo Moving %SRC_DIR% to %WORKDIR% ...
echo =============================================================
robocopy "%SRC_DIR%" "%WORKDIR%" /E /MOVE /TEE /LOG+:"%LOGFILE%"

REM /TEE でログをコンソールにも表示
if %ERRORLEVEL% GEQ 8 (
    echo ? Robocopy detected errors. Check log: %LOGFILE%
    pause
    exit /b 1
)

echo.
echo =============================================================
echo Move completed. Running benchmark_test.exe...
echo =============================================================
cd /d "%WORKDIR%"

REM --- 実行 ---
"%WORKDIR%\benchmark_test.exe"

REM --- デスクトップにショートカット作成 ---
set "DESKTOP=%USERPROFILE%\Desktop"
set "EXE_PATH=%WORKDIR%\benchmark_test.exe"
set "SHORTCUT_PATH=%DESKTOP%\benchmark_test.lnk"

echo Creating shortcut on Desktop...
powershell -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; ^
    $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); ^
    $Shortcut.TargetPath = '%EXE_PATH%'; ^
    $Shortcut.WorkingDirectory = '%WORKDIR%'; ^
    $Shortcut.Save()"

echo Shortcut created: %SHORTCUT_PATH%
echo.
pause
