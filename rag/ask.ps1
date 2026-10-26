<#
.SYNOPSIS
    Atajo para consultar el RAG local con la consola en UTF-8.

.DESCRIPTION
    PowerShell decodifica la salida de los procesos hijos con la codepage activa
    (cp850/cp1252 en Windows), lo que rompe tildes y símbolos. Este wrapper fija
    la consola en UTF-8 y reenvía todos los argumentos a rag\query.py.

.EXAMPLE
    .\rag\ask.ps1 "¿Qué VLAs usan ROS 2 nativamente?" -k 5

.EXAMPLE
    .\rag\ask.ps1 "tactile sensing" --prompt --export rag\out\contexto.md

.NOTES
    No usa ni guarda credenciales: el índice y los embeddings son 100 % locales.
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$QueryArgs
)

$ErrorActionPreference = "Stop"

# Consola en UTF-8 para que las tildes y los símbolos lleguen intactos.
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {
    Write-Warning "No se pudo fijar UTF-8 en la consola: $($PSItem.Exception.Message)"
}

$ragDir = Split-Path -Parent $PSCommandPath
$python = Join-Path $ragDir ".venv\Scripts\python.exe"
$query  = Join-Path $ragDir "query.py"

if (-not (Test-Path $python)) {
    Write-Error "No existe el entorno virtual. Crealo con:  py -3.14 -m venv '$ragDir\.venv'  e instala requirements.txt"
    exit 1
}
if (-not (Test-Path $query)) {
    Write-Error "No se encuentra '$query'."
    exit 1
}

& $python $query @QueryArgs
exit $LASTEXITCODE
