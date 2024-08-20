@echo off

echo --------------------
echo Super Usuario Django
echo --------------------

:: Ingresar al Directorio del Proyecto
cd ..

:: Activar Entorno Virtual de Python
call .\.venv\Scripts\activate.bat

echo Crear Super-Usuario en Django
python manage.py createsuperuser
echo.

echo Abrir el Administrador de Django en el Navegador
start http://localhost:8000/admin

echo Iniciar Servidor
python manage.py runserver