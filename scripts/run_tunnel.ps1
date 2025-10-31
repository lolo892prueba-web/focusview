<#
run_tunnel.ps1

Ejecuta un túnel temporal que expone http://localhost:5000 en una URL pública (trycloudflare.com).

USO:
  powershell -ExecutionPolicy Bypass -File .\scripts\run_tunnel.ps1

Esto requiere que ya hayas hecho `cloudflared tunnel login` y creado un túnel o que uses el comando run (sin crear túnel) que usa credenciales en ~/.cloudflared.
#>

$installPath = "C:\Program Files\cloudflared"
$exe = "$installPath\cloudflared.exe"

if(-not (Test-Path -Path $exe)){
    Write-Host "cloudflared no encontrado en $exe. Ejecuta primero scripts\setup_cloudflared.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Iniciando túnel temporal (pulsa CTRL+C en la ventana para detener)":
& $exe tunnel run --url http://localhost:5000
