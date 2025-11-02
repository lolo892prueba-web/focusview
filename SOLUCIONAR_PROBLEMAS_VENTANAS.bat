@echo off
title FocusView - Solucionar Problemas de Ventanas
color 0C

echo.
echo ================================================
echo   FOCUSVIEW - SOLUCIONAR PROBLEMAS DE VENTANAS
echo ================================================
echo.

cd /d "%~dp0"

echo 🔍 DIAGNÓSTICO DE PROBLEMAS:
echo.

echo 1. Verificando puertos en uso...
echo.

echo Puerto 5000 (Flask):
netstat -an | findstr :5000
if %errorlevel% equ 0 (
    echo ✅ Puerto 5000 está en uso (Flask funcionando)
) else (
    echo ❌ Puerto 5000 NO está en uso (Flask no funcionando)
)

echo.
echo Puerto 5500 (Live Server):
netstat -an | findstr :5500
if %errorlevel% equ 0 (
    echo ⚠️ Puerto 5500 está en uso (Live Server activo)
) else (
    echo ✅ Puerto 5500 está libre
)

echo.
echo Puerto 5001 (Live Server alternativo):
netstat -an | findstr :5001
if %errorlevel% equ 0 (
    echo ⚠️ Puerto 5001 está en uso (Live Server alternativo)
) else (
    echo ✅ Puerto 5001 está libre
)

echo.
echo ================================================
echo   SOLUCIONES DISPONIBLES
echo ================================================
echo.

echo Selecciona qué problema quieres solucionar:
echo.
echo 1. Detener Live Server (puertos 5500 y 5001)
echo 2. Iniciar servidor Flask (puerto 5000)
echo 3. Reiniciar todo (detener + iniciar)
echo 4. Abrir páginas directamente en puerto 5000
echo 5. Verificar configuración de VS Code
echo 6. Salir
echo.

set /p choice="Ingresa tu opción (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🛑 Deteniendo Live Server...
    
    echo Deteniendo procesos en puerto 5500...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5500') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    
    echo Deteniendo procesos en puerto 5001...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    
    echo ✅ Live Server detenido
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo 🚀 Iniciando servidor Flask...
    echo.
    echo Presiona Ctrl+C para detener el servidor
    echo.
    python app.py
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo 🔄 Reiniciando todo...
    
    echo Deteniendo Live Server...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5500') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    
    timeout /t 2 /nobreak >nul
    
    echo Iniciando servidor Flask...
    start "FocusView Flask Server" python app.py
    
    timeout /t 3 /nobreak >nul
    
    echo Abriendo páginas en puerto 5000...
    start "" "http://localhost:5000"
    
    echo ✅ Todo reiniciado correctamente
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo 🌐 Abriendo páginas directamente en puerto 5000...
    
    start "" "http://localhost:5000"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/explorar"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/login"
    
    echo ✅ Páginas abiertas en puerto 5000
    goto :end
)

if "%choice%"=="5" (
    echo.
    echo ⚙️ Verificando configuración de VS Code...
    
    if exist ".vscode\settings.json" (
        echo ✅ Archivo de configuración encontrado
        echo.
        echo Contenido actual:
        type ".vscode\settings.json"
    ) else (
        echo ❌ Archivo de configuración NO encontrado
        echo Creando configuración por defecto...
        
        mkdir ".vscode" 2>nul
        echo { > ".vscode\settings.json"
        echo     "liveServer.settings.port": 5001, >> ".vscode\settings.json"
        echo     "liveServer.settings.donotShowInfoMsg": true >> ".vscode\settings.json"
        echo } >> ".vscode\settings.json"
        
        echo ✅ Configuración creada
    )
    goto :end
)

if "%choice%"=="6" (
    echo Saliendo...
    goto :end
)

echo Opción inválida. Saliendo...

:end
echo.
echo ================================================
echo   RESUMEN
echo ================================================
echo.
echo 💡 CONSEJOS PARA EVITAR PROBLEMAS:
echo.
echo 1. SIEMPRE usa el puerto 5000 para FocusView
echo 2. Cierra Live Server en VS Code cuando trabajes con Flask
echo 3. El script de redirección automática ya está configurado
echo 4. Si hay problemas, ejecuta este script nuevamente
echo.
pause




