@echo off

echo ----------------------------------------------------
echo Script para añadir MySQL de XAMPP al PATH en Windows
echo ----------------------------------------------------

set "mysqlPath=C:\xampp\mysql\bin"

REM Verifica si la ruta ya está en el PATH

echo %PATH% | find /I "%mysqlPath%" >nul
if %ERRORLEVEL%==0 (
    echo La ruta de MySQL de XAMPP ya está en el PATH del sistema.
) else (
    REM Agregar la ruta al PATH
    setx /M PATH "%PATH%;%mysqlPath%"
    echo La ruta de MySQL de XAMPP ha sido añadida al PATH del sistema.
)

echo.
echo PARA SALIR PRESIONA UNA TECLA.
pause > nul
exit
