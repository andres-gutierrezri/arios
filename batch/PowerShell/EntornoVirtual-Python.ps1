# -----------------------------------------------
# Iniciar Entorno Virtual de Python en PowerShell
# -----------------------------------------------

# Definir el archivo o carpeta marcador que existe en la raíz del proyecto
# Puedes usar cualquier archivo o carpeta que solo exista en la raíz del proyecto
$rootIdentifier = ".venv" # Reemplaza con tu archivo o carpeta marcador

# Comienza desde el directorio actual
$currentDir = Get-Location

# Función para buscar la carpeta raíz
function Find-ProjectRoot {
    param (
        [string]$dir
    )
    # Verifica si el archivo identificador está en el directorio actual
    if (Test-Path (Join-Path $dir $rootIdentifier)) {
        return $dir
    }
    # Si estamos en la unidad raíz, se detiene la búsqueda
    if ($dir -eq [System.IO.Path]::GetPathRoot($dir)) {
        return $null
    }
    # Sube un nivel en el árbol de directorios
    return Find-ProjectRoot (Get-Item $dir).Parent.FullName
}

# Busca la carpeta raíz
$projectRoot = Find-ProjectRoot $currentDir.Path

if ($projectRoot) {
    # Cambia el directorio a la carpeta raíz
    Set-Location $projectRoot
    Write-Output "Navegado a la carpeta raiz del proyecto: $projectRoot"
} else {
    Write-Output "No se pudo encontrar la carpeta raiz del proyecto."
}

# Iniciar Entorno Virtual de Python
write-Output "Iniciar Entorno Virtual de Python en PowerShell"
.\.venv\Scripts\activate