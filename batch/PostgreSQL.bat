@echo off

echo ------------------------
echo Base de Datos PostgreSQL
echo ------------------------

echo Ingresar a la Consola de PostgreSQL
C:
cd "C:\Program Files\PostgreSQL\13\scripts"
echo psql -h localhost -U postgres -p 5432 -d postgres
.\runpsql.bat