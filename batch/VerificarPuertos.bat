@echo off

echo -----------------
echo Verificar Puertos
echo -----------------

netstat -a -p TCP -n

echo.
echo PARA SALIR PRESIONA UNA TECLA.
pause > nul
exit