@echo off

echo ----------------------------------
echo Base de Datos PostgreSQL - Railway
echo ----------------------------------

echo Ingresar a la Consola de PostgreSQL - Railway

REM Establecer la contraseña de PostgreSQL en la variable de entorno PGPASSWORD
set PGPASSWORD=eMLfleYhXatpSQYnODGxMzbcXkIYysya

REM Conectar a la base de datos PostgreSQL utilizando psql
psql -h junction.proxy.rlwy.net -U postgres -p 11211 -d postgres

REM Limpiar la variable de entorno PGPASSWORD por seguridad
set PGPASSWORD=
