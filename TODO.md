# TODO: Desplegar FocusView con HTTPS gratis en focusview.io

## Información Recopilada
- Proyecto Flask con frontend HTML/CSS/JS.
- Usuario quiere HTTPS gratis con certificado SSL avanzado (DV via Let's Encrypt).
- Repo nuevo: https://github.com/lolo892prueba-web/FocusView.io.git
- Dominio: focusview.io

## Plan
- Eliminar archivos innecesarios para simplificar.
- Separar frontend (HTML/CSS/JS) y backend (Flask).
- Desplegar frontend en GitHub Pages (HTTPS gratis).
- Desplegar backend en Render (HTTPS gratis).
- Configurar DNS de focusview.io para apuntar a GitHub Pages y Render.

## Archivos a eliminar
- deploy/ (VPS)
- package/ (Cloudflare Workers)
- scripts/ (túneles y setup)
- Archivos .bat: ABRIR_EN_PUERTO_5000.bat, AUTO_INICIAR_FLASK.bat, CONFIGURAR_FIREWALL_AUTO.bat, CONFIGURAR_NOIP.bat, DIAGNOSTICO_ERRORES.bat, INICIAR_SERVIDOR.bat, INSTALAR_SERVICIO_24H_MEJORADO.bat, SOLUCIONAR_PROBLEMAS_VENTANAS.bat
- Otros: FocusView_Database_Schema.sql, local_users.db, __pycache__/, .qodo/, .vscode/

## Dependientes
- Ninguno

## Followup steps
- Probar app Flask localmente después de eliminación.
- Crear repositorio separado para frontend.
- Desplegar frontend en GitHub Pages.
- Desplegar backend en Render.
- Configurar DNS de focusview.io.
