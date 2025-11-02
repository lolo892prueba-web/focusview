@echo off
title FocusView - Auto Start Flask Server
color 0A

echo.
echo ================================================
echo   FOCUSVIEW - INICIANDO AUTOMÁTICAMENTE
echo ================================================
echo.

cd /d "%~dp0"

echo 🔍 Verificando si el servidor Flask ya está ejecutándose...
netstat -an | findstr :5000 >nul
if %errorlevel% equ 0 (
    echo ✅ Servidor Flask ya está ejecutándose en puerto 5000
    echo.
    echo 🌐 Abriendo páginas automáticamente...
    start "" "http://localhost:5000"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/explorar"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/login"
    echo.
    echo ✅ Páginas abiertas correctamente
    echo.
    echo 💡 El servidor Flask ya estaba ejecutándose
    echo 💡 Las páginas se han abierto automáticamente
    echo.
    pause
    exit /b 0
)

echo ⚠️ Servidor Flask NO está ejecutándose
echo.
echo 🚀 Iniciando servidor Flask automáticamente...
echo.

echo Verificando dependencias de Python...
python -c "import flask, flask_cors, pyodbc" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: Faltan dependencias de Python
    echo.
    echo Instalando dependencias automáticamente...
    pip install flask flask-cors pyodbc
    if %errorlevel% neq 0 (
        echo ❌ Error al instalar dependencias
        echo.
        echo Por favor instala manualmente:
        echo pip install flask flask-cors pyodbc
        echo.
        pause
        exit /b 1
    )
    echo ✅ Dependencias instaladas correctamente
)

echo.
echo 🚀 Iniciando servidor Flask...
echo.
echo ⚠️ IMPORTANTE: 
echo    - El servidor se iniciará en segundo plano
echo    - Las páginas se abrirán automáticamente
echo    - Para detener el servidor, cierra esta ventana
echo.

start "FocusView Flask Server" python app.py

echo Esperando que el servidor se inicie...
timeout /t 5 /nobreak >nul

echo Verificando que el servidor esté funcionando...
netstat -an | findstr :5000 >nul
if %errorlevel% equ 0 (
    echo ✅ Servidor Flask iniciado correctamente
    echo.
    echo 🌐 Abriendo páginas automáticamente...
    start "" "http://localhost:5000"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/explorar"
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000/login"
    echo.
    echo ✅ ¡Todo listo! Las páginas están abiertas
    echo.
    echo 💡 CONSEJO: 
    echo    - El servidor Flask está ejecutándose en segundo plano
    echo    - Puedes cerrar esta ventana cuando quieras
    echo    - Para detener el servidor, busca "FocusView Flask Server" en el administrador de tareas
    echo.
) else (
    echo ❌ Error: No se pudo iniciar el servidor Flask
    echo.
    echo Por favor ejecuta manualmente:
    echo python app.py
    echo.
)

pause




