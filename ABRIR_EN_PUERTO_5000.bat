@echo off
title FocusView - Abrir en Puerto 5000
color 0A

echo.
echo ================================================
echo   FOCUSVIEW - ABRIENDO EN PUERTO 5000
echo ================================================
echo.

cd /d "%~dp0"

echo Verificando que el servidor Flask esté ejecutándose...
netstat -an | findstr :5000 >nul
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: El servidor Flask NO está ejecutándose en el puerto 5000
    echo.
    echo Para solucionarlo:
    echo 1. Ejecuta primero: INICIAR_SERVIDOR.bat
    echo 2. O ejecuta: python app.py
    echo 3. Luego ejecuta este archivo nuevamente
    echo.
    pause
    exit /b 1
)

echo ✅ Servidor Flask detectado en puerto 5000
echo.

echo ================================================
echo   OPCIONES DE ACCESO
echo ================================================
echo.
echo Selecciona qué página quieres abrir:
echo.
echo 1. Página Principal (index.html)
echo 2. Página de Exploración (Explorar.html)  
echo 3. Página de Login (login.html)
echo 4. Abrir todas las páginas en una sola ventana
echo 5. Abrir todas las páginas en ventanas separadas
echo 6. Salir
echo.

set /p choice="Ingresa tu opción (1-6): "

if "%choice%"=="1" (
    echo Abriendo página principal...
    start "" "http://localhost:5000"
    goto :end
)

if "%choice%"=="2" (
    echo Abriendo página de exploración...
    start "" "http://localhost:5000/explorar"
    goto :end
)

if "%choice%"=="3" (
    echo Abriendo página de login...
    start "" "http://localhost:5000/login"
    goto :end
)

if "%choice%"=="4" (
    echo Abriendo todas las páginas en una sola ventana...
    start "" "http://localhost:5000"
    timeout /t 3 /nobreak >nul
    echo Navegando a explorar...
    start "" "http://localhost:5000/explorar"
    timeout /t 3 /nobreak >nul
    echo Navegando a login...
    start "" "http://localhost:5000/login"
    goto :end
)

if "%choice%"=="5" (
    echo Abriendo todas las páginas en ventanas separadas...
    start "" "http://localhost:5000"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/explorar"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/login"
    goto :end
)

if "%choice%"=="6" (
    echo Saliendo...
    goto :end
)

echo Opción inválida. Saliendo...

:end
echo.
echo ✅ Páginas abiertas en el puerto 5000 correctamente
echo.
echo 💡 CONSEJO: Para evitar problemas con ventanas nuevas:
echo    - Usa siempre el puerto 5000
echo    - El script de redirección automática ya está configurado
echo    - Si se abre en otro puerto, se redirigirá automáticamente
echo.
pause
