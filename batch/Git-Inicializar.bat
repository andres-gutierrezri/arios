@echo off
setlocal
chcp 65001 > nul

echo ------------------------------------
echo Inicializar Control de Versiones Git
echo ------------------------------------
echo.

REM Ingresar al Directorio del Proyecto
REM Regresar a la carpeta raíz del proyecto subiendo en los directorios

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

REM Establecer las variable de entorno para Git
set GIT_MAIN_BRANCH=%GIT_MAIN_BRANCH%
set GIT_USER_NAME="%GIT_USER_NAME%"
set GIT_USER_EMAIL="%GIT_USER_EMAIL%"
set GIT_REMOTE_REPOSITORY=%GIT_REMOTE_REPOSITORY%
set GIT_FIRST_COMMIT="%GIT_FIRST_COMMIT%"

echo Verificar si Git esta instalado en el sistema
git --version

IF ERRORLEVEL 1 (
    echo Error: Git no esta instalado en el sistema.
    echo.
    exit /b 1
) ELSE (
    echo Git esta instalado en el sistema.
    echo.
)

REM Configurar nombre de usuario y correo electrónico para Git
git config --global user.name %GIT_USER_NAME%
git config --global user.email %GIT_USER_EMAIL%

echo Configuracion de Git
git config --list
echo.

echo Usuario de Git
git config user.name
git config user.email
echo.

echo Inicializar Repositorio Local de Git
git init
echo.

REM Agregar Archivos al Repositorio Local de Git
git add .

echo Confirmar Cambios en el Repositorio Local de Git
git commit -m %GIT_FIRST_COMMIT%
echo.

REM Crear Rama Principal del Repositorio Local de Git
git branch -M %GIT_MAIN_BRANCH%

REM Conectar Repositorio Local de Git con el Repositorio Remoto
git remote add origin %GIT_REMOTE_REPOSITORY%

echo Subir Cambios al Repositorio Remoto
git push -u origin %GIT_MAIN_BRANCH%
echo.

echo ------------------
echo Proceso Finalizado
echo ------------------
echo.

echo PARA SALIR PRESIONA UNA TECLA.
endlocal
pause > nul
exit