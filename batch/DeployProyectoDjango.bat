@echo off

echo ------------------------------------
echo Migraciones y Ejecucion del Proyecto
echo ------------------------------------

:: Ingresar al Directorio del Proyecto
cd ..

:: Activar Entorno Virtual de Python
call .\.venv\Scripts\activate.bat

:: Correr aplicaciones estaticas
:: Copiar todos los archivos estaticos del proyecto en un solo directorio
python manage.py collectstatic
echo.

:: Migraciones del Proyecto
python manage.py makemigrations
echo.
python manage.py migrate
echo.

echo Abrir el Proyecto en el Navegador
start http://localhost:8000/
:: start https://arios-eva.up.railway.app/

:: Correr la Interfaz de Pasarela del Servidor Web, o Web Server Gateway
:: gunicorn EVA.wsgi:application --workers 3 --log-file -

echo Iniciar Servidor
python manage.py runserver