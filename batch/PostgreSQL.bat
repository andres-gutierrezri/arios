@echo off
setlocal
chcp 65001 > nul

echo ------------------------
echo Base de Datos PostgreSQL
echo ------------------------

echo Ingresar a la Consola de PostgreSQL
C:
cd "C:\Program Files\PostgreSQL\16\scripts"
echo psql -h localhost -U postgres -p 5432 -d postgres
.\runpsql.bat

endlocal