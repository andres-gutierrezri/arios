@echo off

echo --------------------------------------------
echo Script para añadir Python al PATH en Windows
echo --------------------------------------------

set "pythonPath=C:\Program Files\Python38"

REM Verifica si la ruta ya está en el PATH

echo %PATH% | find /I "%pythonPath%" >nul
if %ERRORLEVEL%==0 (
    echo La ruta de Python ya está en el PATH del sistema.
) else (
    REM Agregar la ruta al PATH
    setx /M PATH "%PATH%;%pythonPath%"
    echo La ruta de Python ha sido añadida al PATH del sistema.
)

REM Comprobar la versión de Python
python --version

echo.
echo PARA SALIR PRESIONA UNA TECLA.
pause > nul
exit
