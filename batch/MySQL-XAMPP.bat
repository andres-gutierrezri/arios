@echo off

echo -----------------------------------
echo Base de Datos MySQL (MariaDB) XAMPP
echo -----------------------------------

echo Abrir el Administrador de la Base de Datos el Navegador
start http://localhost/phpmyadmin/
echo.

echo Ingresar a la Consola de MySQL XAMPP
C:
cd C:\xampp\mysql\bin
mysql -u root -p -h localhost -P 3306 -D mysql