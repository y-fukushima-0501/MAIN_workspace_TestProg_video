@echo off
REM =============================================================
REM CuPy�p �ꎞ�t�H���_�E���s�p�o�b�`�i_internal�܂ށj
REM =============================================================

set "TEMP=C:\cupy_temp"
set "TMP=C:\cupy_temp"
set "WORKDIR=C:\cupy_run"
set "SRC_DIR=C:\Users\�^�P�b�N�X�� �݌v��\Desktop\benchmark_test"
set "LOGFILE=%WORKDIR%\move_log.txt"

REM --- �ꎞ�t�H���_�쐬 ---
if not exist "%TEMP%" mkdir "%TEMP%"
if not exist "%WORKDIR%" mkdir "%WORKDIR%"

REM --- �t�H���_�ۂ��ƈړ��irobocopy�j ---
echo =============================================================
echo Moving %SRC_DIR% to %WORKDIR% ...
echo =============================================================
robocopy "%SRC_DIR%" "%WORKDIR%" /E /MOVE /TEE /LOG+:"%LOGFILE%"

REM /TEE �Ń��O���R���\�[���ɂ��\��
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

REM --- ���s ---
"%WORKDIR%\benchmark_test.exe"

REM --- �f�X�N�g�b�v�ɃV���[�g�J�b�g�쐬 ---
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
