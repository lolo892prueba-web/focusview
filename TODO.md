# TODO: Configurar HTTPS con Cloudflare Tunnel para FocusView

## Información Recopilada
- Aplicación Flask corriendo en localhost:5000
- Nuevo dominio: focusview.com (IP: 104.247.81.99)
- Scripts existentes: setup_cloudflared.ps1, run_tunnel.ps1
- Cloudflare Tunnel proporciona HTTPS gratuito con certificado SSL avanzado

## Plan de Implementación
1. [x] Actualizar todas las referencias de IPs y dominios:
   - [x] Cambiar 170.245.166.31 → 104.247.81.99
   - [x] Cambiar focusview.is-cool.dev → focusview.com
   - [x] Actualizar documentación y scripts

2. [x] Configurar Cloudflare Tunnel para focusview.com:
   - [x] Instalar cloudflared usando winget
   - [x] Autenticar con Cloudflare (cloudflared tunnel login)
   - [x] Crear túnel (cloudflared tunnel create focusview-tunnel)
   - [x] Configurar DNS para focusview.com (cloudflared tunnel route dns)
   - [x] Ejecutar el túnel (cloudflared tunnel run --url http://localhost:5000)
   - [x] Verificar HTTPS en https://focusview.com

3. [x] Actualizar archivos dependientes:
   - [x] scripts/setup_cloudflared.ps1 (modificar para usar winget)
   - [x] scripts/run_tunnel.ps1 (actualizar para túnel nombrado)
   - [x] README.md, INICIAR_SERVIDOR.bat, CONFIGURAR_NOIP.bat

## Archivos Dependientes
- scripts/setup_cloudflared.ps1
- scripts/run_tunnel.ps1
- README.md
- INICIAR_SERVIDOR.bat
- CONFIGURAR_NOIP.bat
- login.html
- FocusView_Database_Schema.sql

## Pasos de Seguimiento
- Asegurar que la app Flask esté corriendo en localhost:5000
- Agregar focusview.com a Cloudflare (si no está)
- Probar acceso HTTPS
- Configurar firewall y router para IP 104.247.81.99
