@echo off

title "%~0"

set PORT=COM3
set ROOT_DIR="%~dp0\root"
set LOG_LEVEL=10

if NOT exist %ROOT_DIR% (
    echo ERROR: %ROOT_DIR% doesn't exists?!?
    echo.
    echo Please create server root dir and put DWEEBS into it.
    echo.
    pause
    exit 1
)

set python=%~dp0\Scripts\python.exe
if NOT exist %python% (
    echo.
    echo ERROR: '%python%' doesn't exists?!?
    echo.
    pause
    exit 1
)

:loop
    cls
    echo on
    %python% -m dwload_server.dwload_server --port=%PORT% --root_dir=%ROOT_DIR% --log_level=%LOG_LEVEL%
    @echo off
    echo.
    pause
goto:loop