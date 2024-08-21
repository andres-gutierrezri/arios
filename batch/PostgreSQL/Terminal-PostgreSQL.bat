@echo off

echo ------------------------
echo Base de Datos PostgreSQL
echo ------------------------

echo Ingresar a la Consola de PostgreSQL - Local

REM Bloque de comentarios
goto comment
C:
cd "C:\Program Files\PostgreSQL\13\scripts"
echo psql -U postgres
.\runpsql.bat
:comment

REM Establecer la contraseña de PostgreSQL en la variable de entorno PG_PASSWORD
set PG_PASSWORD=postgresql

REM Conectar a la base de datos PostgreSQL utilizando psql
psql -h localhost -U postgres -p 5432 -d postgres

REM Limpiar la variable de entorno PG_PASSWORD por seguridad
set PG_PASSWORD=