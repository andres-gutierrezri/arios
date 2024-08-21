# -----------------------------------------------
# Habilitar la Ejecución de Scripts en PowerShell
# -----------------------------------------------

<#
    Script que habilita la ejecución de scripts en PowerShell.
    Para ejecutar este script, se debe ejecutar PowerShell con permisos de administrador.
#>

write-Output "Habilitar la Ejecucion de Scripts para el Usuario Actual en PowerShell"

Set-ExecutionPolicy -Scope CurrentUser Unrestricted -Force # Directiva de ejecución para el usuario actual
Get-ExecutionPolicy # Debe mostrar Unrestricted
Get-ExecutionPolicy -List

cmd /c pause