@echo off
setlocal
chcp 65001 > nul

echo --------------
echo Crear Proyecto
echo --------------

REM Ingresar al Directorio del Proyecto
REM Regresar a la carpeta raíz del Proyecto subiendo en los directorios

REM Definir el nombre del archivo marcador que existe en la raíz del Proyecto
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
echo No se pudo encontrar la carpeta raiz del Proyecto.
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

REM Establecer las variable de entorno para el Proyecto
set PROJECT_NAME=%PROJECT_NAME%
set APP_NAME_1=%APP_NAME_1%

REM Activar Entorno Virtual de Python
call .\.venv\Scripts\activate.bat

REM Verificar si la activación fue correcta comprobando la versión de Python
python --version

IF ERRORLEVEL 1 (
    echo Error: No se pudo activar el entorno virtual de Python
    exit /b 1
) ELSE (
    echo Entorno virtual de Python activado correctamente.
)

REM Crear Proyecto de Django
django-admin startproject %PROJECT_NAME%
cd %PROJECT_NAME%
echo.

REM Mover el Archivo manage.py al Directorio del Proyecto
set "archivo=manage.py"

REM Obtener la Ruta del Directorio Actual
set "ruta_actual=%cd%"

REM Mover el Archivo manage.py a la Carpeta Anterior
move "%ruta_actual%\%archivo%" "%ruta_actual%\..\"

REM Ingresar al Directorio del Proyecto
cd %PROJECT_NAME%

REM Obtener la Ruta del Directorio Actual
set "ruta_actual=%cd%"

REM Mover Todos los Archivos de la Carpeta Actual a la Carpeta Anterior
move "%ruta_actual%\*.*" "%ruta_actual%\..\"

REM Eliminar la Carpeta Actual
cd ..
rmdir /s /q %PROJECT_NAME%

REM Crear Aplicaciones Dentro del Proyecto
cd ..
python manage.py startapp %APP_NAME_1%
echo.

echo ------------------
echo Proceso Finalizado
echo ------------------
echo.

echo PARA SALIR PRESIONA UNA TECLA.
endlocal
pause > nul
exit