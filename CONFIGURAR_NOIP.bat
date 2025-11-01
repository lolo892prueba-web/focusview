@echo off
title Configurando Dominio Gratuito con NO-IP
color 0B

echo.
echo ================================================
echo   CONFIGURANDO DOMINIO GRATUITO CON NO-IP
echo ================================================
echo.

cd /d "%~dp0"

echo Tu IP publica es: 104.247.81.99
echo.

echo ================================================
echo   PASOS PARA CONFIGURAR DOMINIO GRATUITO
echo ================================================
echo.
echo 1. Ve a: https://www.noip.com
echo 2. Crea una cuenta gratuita
echo 3. Inicia sesion
echo 4. Ve a "My Services" -> "Dynamic DNS"
echo 5. Crea un nuevo hostname:
echo    - Hostname: focusview
echo    - Domain: ddns.net
echo    - Direccion IP: 104.247.81.99
echo 6. Guarda la configuracion
echo.
echo Tu dominio sera: http://focusview.ddns.net:5000
echo.
echo ================================================
echo   CONFIGURACION DEL ROUTER
echo ================================================
echo.
echo 1. Accede a tu router: http://192.168.1.1
echo 2. Busca "Port Forwarding" o "Redireccion de puertos"
echo 3. Configura:
echo    - Puerto externo: 5000
echo    - Puerto interno: 5000
echo    - IP interna: 192.168.1.3 (tu IP local)
echo    - Protocolo: TCP
echo 4. Guarda la configuracion
echo.
echo ================================================
echo   CONFIGURACION DEL FIREWALL
echo ================================================
echo.
echo 1. Abre Windows Defender Firewall
echo 2. Ve a "Configuracion avanzada"
echo 3. Reglas de entrada -> Nueva regla
echo 4. Puerto -> TCP -> Puerto especifico: 5000
echo 5. Permitir conexion -> Aplicar a todos los perfiles
echo 6. Nombre: FocusView Server
echo.
echo ================================================
echo   VERIFICACION
echo ================================================
echo.
echo Una vez configurado todo:
echo 1. Tu dominio sera: http://focusview.ddns.net:5000
echo 2. Podras acceder desde cualquier parte del mundo
echo 3. El servidor estara activo 24/7
echo.
echo ¿Quieres abrir NO-IP ahora para configurar el dominio? (S/N)
set /p abrir_noip=

if /i "%abrir_noip%"=="S" (
    echo Abriendo NO-IP...
    start https://www.noip.com
    echo.
    echo Despues de configurar el dominio, ejecuta:
    echo INICIAR_CON_DOMINIO.bat
) else (
    echo Puedes configurar el dominio mas tarde.
    echo Ejecuta este script cuando estes listo.
)

echo.
pause





