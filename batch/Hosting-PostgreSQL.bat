@echo off

echo ----------------------------------
echo Base de Datos PostgreSQL - Railway
echo ----------------------------------

echo Ingresar a la Consola de PostgreSQL - Railway

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

REM Establecer la variable de entorno para PostgreSQL
for /f "tokens=1,2 delims==" %%a in (%ENV_FILE%) do (
    if "%%a"=="POSTGRESQL_DATABASE_URL" (
        set POSTGRESQL_DATABASE_URL=%%b
    )
)

REM Conectar a la base de datos PostgreSQL utilizando psql
psql %POSTGRESQL_DATABASE_URL%