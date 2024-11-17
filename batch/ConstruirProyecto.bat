@echo off
setlocal
chcp 65001 > nul

echo -----------------------------------
echo PYTHON 3 + Entorno Virtual + Django
echo -----------------------------------

echo Version de Python y PIP
python --version
python -m pip --version
pip cache purge
echo.

:: Actualizar PIP
echo Actualizar PIP
python.exe -m pip install --upgrade pip --no-cache-dir
echo.

echo ------------------------
echo Instalar Entorno Virtual
echo ------------------------

pip install --upgrade virtualenv --no-cache-dir
echo.

echo ---------------------
echo Crear Entorno Virtual
echo ---------------------

:: Ingresar al Directorio del Proyecto
cd ..

:: Crear Entorno Virtual
python -m venv .venv
echo Entorno Virtual Creado
echo.

echo -----------------------
echo Activar Entorno Virtual
echo -----------------------

call .\.venv\Scripts\activate.bat

:: Verificar si la activación fue correcta comprobando la versión de Python
python --version
IF ERRORLEVEL 1 (
    echo Error: No se pudo activar el entorno virtual de Python
    exit /b 1
) ELSE (
    echo Entorno virtual de Python activado correctamente.
)

:: Verificar si pip está disponible
pip --version
IF ERRORLEVEL 1 (
    echo Error: pip no esta disponible en el entorno virtual de Python.
    exit /b 1
) ELSE (
    echo pip esta disponible en el entorno virtual de Python.
)

:: Lista de Paquetes Instalados (PIP Python)
echo.
pip list
echo.

echo ---------------------
echo Instalar Dependencias
echo ---------------------

:: Actualizar PIP en el Entorno Virtual
echo Actualizar PIP Entorno Virtual
python.exe -m pip install --upgrade pip --no-cache-dir
echo.

:: Instalar Dependencias para el Proyecto
pip install -r requirements.txt --no-cache-dir
echo.

echo -----------------
echo Version de Django
echo -----------------

:: Version de Django
python -m django --version
echo.

echo -----------------------------------
echo Lista de Paquetes Instalados en PIP
echo -----------------------------------

:: Lista de Paquetes Instalados (PIP Python) 
pip list
echo.

echo ------------------
echo Proceso Finalizado
echo ------------------
echo.

echo PARA SALIR PRESIONA UNA TECLA.
endlocal
pause > nul
exit