@echo off
setlocal
chcp 65001 > nul

echo ----------------------------------
echo Base de Datos PostgreSQL - Hosting
echo ----------------------------------

echo Ingresar a la Consola de PostgreSQL - Hosting

REM Ingresar al Directorio del Proyecto
cd ..

REM Leer variables del archivo .env
REM Establecer la ruta al archivo .env
set ENV_FILE=.env

REM Activar expansión retardada de variables
setlocal enabledelayedexpansion

REM Verificar si el archivo .env existe
if not exist %ENV_FILE% (
    echo El archivo %ENV_FILE% no existe.
    exit /b 1
)

REM Leer cada línea del archivo .env y establecer las variables de entorno
for /f "tokens=1,* delims==" %%a in (%ENV_FILE%) do (
    REM Guardar el valor de la variable
    set "var=%%b"
    
    REM Eliminar comillas dobles si existen
    set "var=!var:"=!"
    
    REM Eliminar comillas simples si existen
    set "var=!var:'=!"

    REM Asignar la variable sin comillas
    set %%a=!var!
)

REM Establecer las variable de entorno para PostgreSQL
set POSTGRESQL_NAME=%POSTGRESQL_HOSTING_DB_NAME%
set POSTGRESQL_USER=%POSTGRESQL_HOSTING_DB_USER%
set POSTGRESQL_HOST=%POSTGRESQL_HOSTING_DB_HOST%
set POSTGRESQL_PORT=%POSTGRESQL_HOSTING_DB_PORT%

REM Establecer la contraseña de PostgreSQL
set PGPASSWORD=%POSTGRESQL_HOSTING_DB_PASSWORD%

REM Conectar a la base de datos PostgreSQL utilizando psql
:: psql -h%POSTGRESQL_HOST% -U%POSTGRESQL_USER% -p%POSTGRESQL_PORT% -d%POSTGRESQL_NAME%
psql -h%POSTGRESQL_HOST% -U%POSTGRESQL_USER% -p%POSTGRESQL_PORT% -d postgres

REM Limpiar la variable de entorno PGPASSWORD por seguridad
set PGPASSWORD=

endlocal