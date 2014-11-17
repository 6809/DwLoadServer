@echo off

title "%~0"

REM ##############################################################################
REM # Edit this for your needs:
set ROOT_DIR="%APPDATA%\dwload-root"

REM # Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL
set LOG_LEVEL=10

REM # Must normaly not changed:
set IP="127.0.0.1"
set PORT=65504
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
    echo Run DWLOAD-Server with Becker Interface
    echo  * root dir: %ROOT_DIR%
    echo  * listen on %IP%:%PORT%
    echo.
    echo on
    python.exe -m dwload_server.dwload_server_cli --root_dir=%ROOT_DIR% --log_level=%LOG_LEVEL% becker --ip=%IP% --port=%PORT%
    @echo off
    echo.
    pause
goto:loop