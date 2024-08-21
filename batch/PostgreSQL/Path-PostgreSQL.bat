@echo off

echo -------------------------------------------------------
echo Script para agregar psql (PostgreSQL) al PATH en Windows
echo -------------------------------------------------------

set "postgresqlBinPath=C:\Program Files\PostgreSQL\13\bin"

REM Verificar si la ruta ya está en el PATH

echo %PATH% | find /I "%postgresqlBinPath%" >nul
if %ERRORLEVEL%==0 (
    echo La ruta de psql ya está en el PATH del sistema.
) else (
    REM Agregar la ruta al PATH
    setx /M PATH "%PATH%;%postgresqlBinPath%"
    echo La ruta de psql ha sido añadida al PATH del sistema.
)

echo.
echo PARA SALIR PRESIONA UNA TECLA.
pause > nul
exit
