@echo off

title "%~0"

REM ##############################################################################
REM # Edit this for your needs:
set PORT=COM3
set ROOT_DIR="%APPDATA%\dwload-root"
set LOG_LEVEL=10
REM ##############################################################################

if NOT exist %ROOT_DIR% (
    echo ERROR: %ROOT_DIR% doesn't exists?!?
    echo.
    echo Please create server root dir and put DWEEBS into it!
    echo.
    pause
    exit 1
)

set activate_bat=%~dp0\Scripts\activate.bat
if NOT exist %activate_bat% (
    echo.
    echo ERROR: '%activate_bat%' doesn't exists?!?
    echo.
    pause
    exit 1
)

call %activate_bat%

:loop
    cls
    echo Run DWLOAD-Server with Serial Interface
    echo  * root dir: %ROOT_DIR%
    echo  * serial port: %PORT%
    echo.
    echo on
    python.exe -m dwload_server.dwload_server_cli --root_dir=%ROOT_DIR% --log_level=%LOG_LEVEL% serial --port=%PORT%
    @echo off
    echo.
    pause
goto:loop