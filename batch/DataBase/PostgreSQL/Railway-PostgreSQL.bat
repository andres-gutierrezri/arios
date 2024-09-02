@echo off

echo ----------------------------------
echo Base de Datos PostgreSQL - Railway
echo ----------------------------------

echo Ingresar a la Consola de PostgreSQL - Railway

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

REM Establecer la variable de entorno para el la base de datos de PostgreSQL
for /f "tokens=1,2 delims==" %%a in (%ENV_FILE%) do (
    if "%%a"=="POSTGRESQL_DATABASE_URL" (
        REM Guardar el valor de la variable
        set "POSTGRESQL_DATABASE_URL=%%b"

        REM Eliminar comillas dobles si existen
        set "POSTGRESQL_DATABASE_URL=!POSTGRESQL_DATABASE_URL:"=!"
        
        REM Eliminar comillas simples si existen
        set "POSTGRESQL_DATABASE_URL=!POSTGRESQL_DATABASE_URL:'=!"

        REM Asignar la variable sin comillas
        set %%a=!POSTGRESQL_DATABASE_URL!
    )
)

REM Conectar a la base de datos PostgreSQL utilizando psql
psql %POSTGRESQL_DATABASE_URL%