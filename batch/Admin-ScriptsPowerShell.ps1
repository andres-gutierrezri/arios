# -----------------------------------------------
# Habilitar la Ejecución de Scripts en PowerShell
# -----------------------------------------------

<#
    Script que habilita la ejecución de scripts en PowerShell.
    Para ejecutar este script, se debe ejecutar PowerShell con permisos de administrador.
#>

# Inicie Windows PowerShell con la opción "Ejecutar como administrador"
write-Output "Habilitar la Ejecucion de Scripts para el Administrador en PowerShell"

Set-ExecutionPolicy -Scope LocalMachine Unrestricted -Force # Directiva de ejecución para el administrador
Get-ExecutionPolicy # Debe mostrar Unrestricted
Get-ExecutionPolicy -List

cmd /c pause