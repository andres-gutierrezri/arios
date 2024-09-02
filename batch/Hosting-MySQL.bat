@echo off

echo -----------------------------
echo Base de Datos MySQL - Railway
echo -----------------------------

echo Ingresar a la Consola de MySQL - Railway

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

REM Establecer las variable de entorno para MySQL Database Hosting
set MYSQL_NAME=%MYSQL_HOSTING_DB_NAME%
set MYSQL_USER=%MYSQL_HOSTING_DB_USER%
set MYSQL_HOST=%MYSQL_HOSTING_DB_HOST%
set MYSQL_PORT=%MYSQL_HOSTING_DB_PORT%

REM Establecer la contraseña de MySQL Database Hosting
set MYSQL_PASSWORD=%MYSQL_HOSTING_DB_PASSWORD%

REM Conectar a la base de datos MySQL utilizando mysql
mysql -u%MYSQL_USER% -p%MYSQL_PASSWORD% -h%MYSQL_HOST% -P%MYSQL_PORT% -D%MYSQL_NAME%

REM Limpiar la variable de entorno MYSQL_PASSWORD por seguridad
set MYSQL_PASSWORD=