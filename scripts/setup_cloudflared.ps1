<#
Setup cloudflared (Windows) - instala usando winget y configura autenticación.

USO: Ejecuta desde PowerShell (puede pedir elevación):
  powershell -ExecutionPolicy Bypass -File .\scripts\setup_cloudflared.ps1

Este script hace:
- Instala cloudflared usando winget (más confiable)
- Lanza `cloudflared tunnel login` para que autorices en el navegador

IMPORTANTE: No puedo ejecutar esto por ti. Ejecuta el script en tu equipo y sigue las instrucciones.
#>

Param()

function Write-Ok($msg){ Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Err($msg){ Write-Host "[ERR] $msg" -ForegroundColor Red }

Write-Host "=> Verificando si winget está disponible..."
try {
    winget --version | Out-Null
    Write-Ok "winget encontrado"
} catch {
    Write-Err "winget no está disponible. Instala Windows Package Manager desde Microsoft Store."
    exit 1
}

Write-Host "=> Instalando cloudflared usando winget..."
try {
    winget install --id Cloudflare.cloudflared --source winget --accept-package-agreements --accept-source-agreements
    Write-Ok "cloudflared instalado exitosamente"
} catch {
    Write-Err "Fallo al instalar cloudflared: $_.Exception.Message"
    exit 1
}

Write-Host "\nSiguiente paso: autenticar cloudflared con tu cuenta de Cloudflare. Se abrirá el navegador para que inicies sesión."
Write-Host "Si no tienes cuenta en Cloudflare, crea una gratis en https://dash.cloudflare.com/"

Write-Host "Ejecutando: cloudflared tunnel login"
cloudflared tunnel login

Write-Host "\nCuando la autenticación termine, crea un túnel para focusview.com:"
Write-Host "  cloudflared tunnel create focusview-tunnel"
Write-Host "  cloudflared tunnel route dns focusview-tunnel focusview.com"
Write-Host "Luego ejecuta el túnel:"
Write-Host "  cloudflared tunnel run focusview-tunnel --url http://localhost:5000"

Write-Host "\nPara HTTPS gratuito en https://focusview.com, asegúrate de que el dominio esté agregado a Cloudflare." -ForegroundColor Yellow
