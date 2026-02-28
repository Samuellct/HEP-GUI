@echo off
echo Building HEP-GUI...
echo.
pyinstaller "%~dp0..\hep_gui.spec" --noconfirm
echo.
if exist "%~dp0..\dist\hep-gui\hep-gui.exe" (
    echo Build OK. Output: dist\hep-gui\
    echo Copy data\ into dist\hep-gui\ before running.
) else (
    echo Build FAILED.
)
pause
