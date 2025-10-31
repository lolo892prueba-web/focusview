@echo off
title FocusView Server - Iniciando con Dominio
color 0A

echo.
echo ================================================
echo   FOCUSVIEW SERVER - INICIANDO CON DOMINIO
echo ================================================
echo.

cd /d "%~dp0"

echo Tu IP publica es: 170.245.166.31
echo Tu IP local es: 192.168.1.3
echo.

echo ================================================
echo   OPCIONES DE ACCESO
echo ================================================
echo.

echo ACCESO LOCAL:
echo - http://localhost:5000
echo - http://127.0.0.1:5000
echo - http://192.168.1.3:5000
echo.

echo ACCESO DESDE INTERNET (una vez configurado):
echo - http://170.245.166.31:5000
echo - http://focusview.ddns.net:5000 (si configuraste NO-IP)
echo - http://focusview.duckdns.org:5000 (si configuraste DuckDNS)
echo.

echo ACCESO CON DOMINIO LOCAL (si configuraste hosts):
echo - http://focusview.com:5000
echo - http://www.focusview.com:5000
echo.

echo ================================================
echo   CONFIGURACION PENDIENTE
echo ================================================
echo.

echo Para tener un dominio real como https://focusview.com:
echo.
echo 1. COMPRAR DOMINIO REAL:
echo    - Ve a: https://www.godaddy.com
echo    - Busca: focusview.com
echo    - Precio: ~$12/año
echo.
echo 2. CONFIGURAR DNS:
echo    - Apunta el dominio a: 170.245.166.31
echo.
echo 3. CONFIGURAR ROUTER:
echo    - Port Forwarding: Puerto 5000
echo.
echo 4. CONFIGURAR FIREWALL:
echo    - Permite puerto 5000
echo.
echo ================================================
echo   INICIANDO SERVIDOR
echo ================================================
echo.

echo Iniciando servidor FocusView...
echo Presiona Ctrl+C para detener
echo.

python app.py

pause