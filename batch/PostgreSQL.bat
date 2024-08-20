@echo off

echo ------------------------
echo Base de Datos PostgreSQL
echo ------------------------

echo Ingresar a la Consola de PostgreSQL
C:
cd "C:\Program Files\PostgreSQL\13\scripts"
echo psql -U postgres
.\runpsql.bat