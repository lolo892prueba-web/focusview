<#
run_tunnel.ps1

Ejecuta un túnel nombrado para focusview.com que expone http://localhost:5000 con HTTPS.

USO:
  powershell -ExecutionPolicy Bypass -File .\scripts\run_tunnel.ps1

Esto requiere que ya hayas hecho `cloudflared tunnel login` y creado el túnel focusview-tunnel.
#>

$exe = "cloudflared"

# Verificar si cloudflared está instalado
try {
    & $exe --version | Out-Null
} catch {
    Write-Host "cloudflared no encontrado. Ejecuta primero scripts\setup_cloudflared.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Iniciando túnel focusview-tunnel (pulsa CTRL+C para detener):"
Write-Host "Esto expondrá http://localhost:5000 en https://focusview.com"
Write-Host ""

& $exe tunnel run focusview-tunnel --url http://localhost:5000
