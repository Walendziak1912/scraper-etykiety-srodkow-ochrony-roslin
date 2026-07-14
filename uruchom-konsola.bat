@echo off
setlocal EnableExtensions

rem Wersja z widoczna konsola – do debugowania / gdy cos nie dziala
cd /d "%~dp0"

where uv >nul 2>&1
if errorlevel 1 (
    echo.
    echo Nie znaleziono narzedzia "uv" w PATH.
    echo Zainstaluj: https://docs.astral.sh/uv/getting-started/installation/
    echo.
    pause
    exit /b 1
)

uv run python main.py
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Aplikacja zakonczyla sie z kodem %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%
