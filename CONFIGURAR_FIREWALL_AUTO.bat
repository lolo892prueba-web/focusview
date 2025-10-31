@echo off
title Configurando Firewall para FocusView
color 0A

echo.
echo ================================================
echo   CONFIGURANDO FIREWALL PARA FOCUSVIEW
echo ================================================
echo.

cd /d "%~dp0"

echo Intentando configurar firewall automaticamente...
echo.

echo Configurando regla de entrada para puerto 5000...
netsh advfirewall firewall add rule name="FocusView Server - Puerto 5000" dir=in action=allow protocol=TCP localport=5000

if %errorlevel% == 0 (
    echo ✅ Regla de entrada configurada exitosamente
) else (
    echo ❌ Error al configurar regla de entrada
    echo Necesitas permisos de administrador
)

echo.
echo Configurando regla de salida para puerto 5000...
netsh advfirewall firewall add rule name="FocusView Server - Puerto 5000 (Salida)" dir=out action=allow protocol=TCP localport=5000

if %errorlevel% == 0 (
    echo ✅ Regla de salida configurada exitosamente
) else (
    echo ❌ Error al configurar regla de salida
    echo Necesitas permisos de administrador
)

echo.
echo ================================================
echo   CONFIGURACION COMPLETADA
echo ================================================
echo.

echo Si las reglas se configuraron correctamente:
echo ✅ Puerto 5000 abierto para conexiones entrantes
echo ✅ Puerto 5000 abierto para conexiones salientes
echo ✅ Tu servidor FocusView puede recibir conexiones
echo.

echo Si hubo errores:
echo ⚠️ Necesitas ejecutar como administrador
echo ⚠️ Haz clic derecho en este archivo
echo ⚠️ Selecciona "Ejecutar como administrador"
echo.

echo Para verificar la configuracion:
echo netsh advfirewall firewall show rule name="FocusView Server - Puerto 5000"
echo.

pause





