@echo off

echo -------------------
echo Base de Datos MySQL
echo -------------------

echo Ingresar a la Consola de MySQL - Local

REM Bloque de comentarios
goto comment
C:
cd "C:\Program Files\MySQL\MySQL Server 9.0\bin"
mysql -u root -p -h localhost -P 3306 -D mysql
:comment

REM Ingresar al Directorio del Proyecto
REM Regresar a la carpeta raíz del proyecto subiendo en los directorios

REM Asegurarse de que la consola esté usando la página de códigos 1252
chcp 1252 >nul

REM Definir el nombre del archivo marcador que existe en la raíz del proyecto
set "marker=.env"

REM Inicializar la variable para guardar la ruta raíz
set "root_dir="

REM Comenzar desde el directorio actual
set "current_dir=%cd%"

:search_root
REM Verificar si el archivo marcador existe en el directorio actual
if exist "%current_dir%\%marker%" (
    set "root_dir=%current_dir%"
    goto :found
)

REM Subir un nivel en el directorio
cd ..

REM Verificar si estamos en la raíz del sistema (no se puede subir más)
if "%cd%"=="%current_dir%" (
    goto :not_found
)

REM Actualizar current_dir y continuar la búsqueda
set "current_dir=%cd%"
goto :search_root

:found
echo Carpeta raiz encontrada en: %root_dir%
cd /d "%root_dir%"
goto :end

:not_found
echo No se pudo encontrar la carpeta raiz del proyecto.
goto :end

:end

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

REM Establecer las variable de entorno para MySQL
set MYSQL_USER=%MYSQL_DB_USER%
set MYSQL_HOST=%MYSQL_DB_HOST%
set MYSQL_PORT=%MYSQL_DB_PORT%

REM Establecer la contraseña de MySQL
set MYSQL_PASSWORD=%MYSQL_DB_PASSWORD%

REM Conectar a la base de datos MySQL utilizando mysql
mysql -u%MYSQL_USER% -p%MYSQL_PASSWORD% -h%MYSQL_HOST% -P%MYSQL_PORT% -D mysql

REM Limpiar la variable de entorno MYSQL_PASSWORD por seguridad
set MYSQL_PASSWORD=