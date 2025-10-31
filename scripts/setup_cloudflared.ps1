<#
Setup cloudflared (Windows) - descarga e inicia el proceso de autenticación.

USO: Ejecuta desde PowerShell (puede pedir elevación para mover archivos a Program Files):
  powershell -ExecutionPolicy Bypass -File .\scripts\setup_cloudflared.ps1

Este script hace:
- Descarga cloudflared.exe a %USERPROFILE%\Downloads
- Crea carpeta C:\Program Files\cloudflared y mueve el binario allí
- Lanza `cloudflared tunnel login` para que autorices en el navegador

IMPORTANTE: No puedo ejecutar esto por ti. Ejecuta el script en tu equipo y sigue las instrucciones.
#>

Param()

function Write-Ok($msg){ Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Err($msg){ Write-Host "[ERR] $msg" -ForegroundColor Red }

$installPath = "C:\Program Files\cloudflared"
$downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$dest = "$env:USERPROFILE\Downloads\cloudflared.exe"

Write-Host "=> Preparando descarga de cloudflared..."
try{
    Invoke-WebRequest -Uri $downloadUrl -OutFile $dest -UseBasicParsing -ErrorAction Stop
    Write-Ok "Descargado a $dest"
} catch {
    Write-Err "Fallo al descargar: $_.Exception.Message"
    exit 1
}

Write-Host "=> Instalando en $installPath (se necesita permisos de administrador para mover a Program Files)"
if(-not (Test-Path -Path $installPath)){
    New-Item -ItemType Directory -Path $installPath -Force | Out-Null
}

try{
    Move-Item -Path $dest -Destination "$installPath\cloudflared.exe" -Force
    Write-Ok "Movido a $installPath\cloudflared.exe"
} catch {
    Write-Err "No se pudo mover el archivo. Ejecuta PowerShell como Administrador y vuelve a intentarlo. Error: $_.Exception.Message"
    exit 1
}

Write-Host "\nSiguiente paso: autenticar cloudflared con tu cuenta de Cloudflare. Se abrirá el navegador para que inicies sesión."
Write-Host "Si no tienes cuenta en Cloudflare, crea una gratis en https://dash.cloudflare.com/"

Write-Host "Ejecutando: cloudflared tunnel login"
& "$installPath\cloudflared.exe" tunnel login

Write-Host "\nCuando la autenticación termine, crea un túnel (ejemplo):"
Write-Host "  cloudflared tunnel create focusview-tunnel"
Write-Host "Luego puedes ejecutar el túnel temporal con:"
Write-Host "  cloudflared tunnel run --url http://localhost:5000"

Write-Host "\nTambién puedo darte pasos para instalar cloudflared como servicio si quieres que el túnel arranque automáticamente." -ForegroundColor Yellow
