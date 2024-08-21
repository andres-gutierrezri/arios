@echo off

echo -----------------------------------
echo Base de Datos MySQL (MariaDB) XAMPP
echo -----------------------------------

echo Abrir el Administrador de la Base de Datos el Navegador
start http://localhost/phpmyadmin/
echo.

echo Ingresar a la Consola de MySQL XAMPP - Local

REM Bloque de comentarios
goto comment
C:
cd C:\xampp\mysql\bin
mysql -u root -p -h localhost
:comment

REM Establecer la contraseña de MySQL XAMPP en la variable de entorno MYSQL_PASSWORD
set MYSQL_PASSWORD=mysql

REM Conectar a la base de datos MySQL XAMPP utilizando mysql
mysql -u root -p%MYSQL_PASSWORD% -h localhost -P 3306 -D mysql

REM Limpiar la variable de entorno MYSQL_PASSWORD por seguridad
set MYSQL_PASSWORD=