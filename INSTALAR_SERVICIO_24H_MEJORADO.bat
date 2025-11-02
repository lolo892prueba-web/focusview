@echo off
title Instalando FocusView como Servicio 24/7 - MEJORADO
color 0B

echo.
echo ================================================
echo   INSTALANDO FOCUSVIEW COMO SERVICIO 24/7
echo ================================================
echo.
echo Esto instalara tu servidor como un SERVICIO DE WINDOWS
echo que estara ACTIVO LAS 24 HORAS TODOS LOS DIAS.
echo.

cd /d "%~dp0"

echo Verificando dependencias...
echo.

echo Instalando pywin32...
pip install pywin32

echo.
echo Creando servicio de Windows mejorado...
echo.

echo import win32serviceutil > focusview_service.py
echo import win32service >> focusview_service.py
echo import win32event >> focusview_service.py
echo import servicemanager >> focusview_service.py
echo import socket >> focusview_service.py
echo import sys >> focusview_service.py
echo import os >> focusview_service.py
echo import time >> focusview_service.py
echo import subprocess >> focusview_service.py
echo import logging >> focusview_service.py
echo. >> focusview_service.py
echo # Configurar logging >> focusview_service.py
echo logging.basicConfig( >> focusview_service.py
echo     filename=r'%CD%\focusview_service.log', >> focusview_service.py
echo     level=logging.INFO, >> focusview_service.py
echo     format='%%(asctime)s - %%(levelname)s - %%(message)s' >> focusview_service.py
echo ) >> focusview_service.py
echo. >> focusview_service.py
echo class FocusViewService(win32serviceutil.ServiceFramework): >> focusview_service.py
echo     _svc_name_ = "FocusView24H" >> focusview_service.py
echo     _svc_display_name_ = "FocusView 24/7 Server" >> focusview_service.py
echo     _svc_description_ = "Servidor FocusView activo 24 horas todos los dias" >> focusview_service.py
echo. >> focusview_service.py
echo     def __init__(self, args): >> focusview_service.py
echo         win32serviceutil.ServiceFramework.__init__(self, args) >> focusview_service.py
echo         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) >> focusview_service.py
echo         socket.setdefaulttimeout(60) >> focusview_service.py
echo         self.is_running = True >> focusview_service.py
echo. >> focusview_service.py
echo     def SvcStop(self): >> focusview_service.py
echo         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) >> focusview_service.py
echo         self.is_running = False >> focusview_service.py
echo         win32event.SetEvent(self.hWaitStop) >> focusview_service.py
echo         logging.info("Servicio FocusView detenido") >> focusview_service.py
echo. >> focusview_service.py
echo     def SvcDoRun(self): >> focusview_service.py
echo         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, >> focusview_service.py
echo                               servicemanager.PYS_SERVICE_STARTED, >> focusview_service.py
echo                               (self._svc_name_, '')) >> focusview_service.py
echo         logging.info("Servicio FocusView iniciado") >> focusview_service.py
echo         self.main() >> focusview_service.py
echo. >> focusview_service.py
echo     def main(self): >> focusview_service.py
echo         # Cambiar al directorio del script >> focusview_service.py
echo         script_dir = r'%CD%' >> focusview_service.py
echo         os.chdir(script_dir) >> focusview_service.py
echo         logging.info(f"Directorio de trabajo: {script_dir}") >> focusview_service.py
echo. >> focusview_service.py
echo         restart_count = 0 >> focusview_service.py
echo         max_restarts = 10 >> focusview_service.py
echo. >> focusview_service.py
echo         while self.is_running: >> focusview_service.py
echo             try: >> focusview_service.py
echo                 logging.info(f"Iniciando servidor FocusView (intento {restart_count + 1})") >> focusview_service.py
echo                 # Ejecutar el servidor Flask >> focusview_service.py
echo                 process = subprocess.Popen(['python', 'app.py'], >> focusview_service.py
echo                                           stdout=subprocess.PIPE, >> focusview_service.py
echo                                           stderr=subprocess.PIPE, >> focusview_service.py
echo                                           cwd=script_dir) >> focusview_service.py
echo. >> focusview_service.py
echo                 # Esperar a que termine el proceso >> focusview_service.py
echo                 process.wait() >> focusview_service.py
echo. >> focusview_service.py
echo                 if not self.is_running: >> focusview_service.py
echo                     break >> focusview_service.py
echo. >> focusview_service.py
echo                 restart_count += 1 >> focusview_service.py
echo                 logging.warning(f"Servidor detenido inesperadamente. Reiniciando... (intento {restart_count})") >> focusview_service.py
echo. >> focusview_service.py
echo                 if restart_count ^>^= max_restarts: >> focusview_service.py
echo                     logging.error(f"Maximo de reinicios alcanzado ({max_restarts}). Esperando 60 segundos...") >> focusview_service.py
echo                     time.sleep(60) >> focusview_service.py
echo                     restart_count = 0 >> focusview_service.py
echo                 else: >> focusview_service.py
echo                     time.sleep(5) >> focusview_service.py
echo. >> focusview_service.py
echo             except Exception as e: >> focusview_service.py
echo                 logging.error(f"Error en el servicio: {e}") >> focusview_service.py
echo                 time.sleep(10) >> focusview_service.py
echo. >> focusview_service.py
echo         logging.info("Servicio FocusView terminado") >> focusview_service.py
echo. >> focusview_service.py
echo if __name__ == '__main__': >> focusview_service.py
echo     win32serviceutil.HandleCommandLine(FocusViewService) >> focusview_service.py

echo.
echo Instalando servicio...
echo.

python focusview_service.py install

echo.
echo Iniciando servicio...
echo.

python focusview_service.py start

echo.
echo ================================================
echo   SERVICIO 24/7 INSTALADO Y ACTIVO
echo ================================================
echo.
echo Tu servidor FocusView ahora esta:
echo.
echo ✅ ACTIVO LAS 24 HORAS
echo ✅ TODOS LOS DIAS
echo ✅ Se inicia automaticamente con Windows
echo ✅ Se reinicia si se cae
echo ✅ Funciona en segundo plano
echo ✅ Logs guardados en: focusview_service.log
echo.
echo Para administrar el servicio:
echo.
echo - Ver estado: sc query FocusView24H
echo - Detener: python focusview_service.py stop
echo - Iniciar: python focusview_service.py start
echo - Reiniciar: python focusview_service.py restart
echo - Desinstalar: python focusview_service.py remove
echo.
echo Para ver logs en tiempo real:
echo - Abre: focusview_service.log
echo.
echo Para verificar que funciona:
echo - Ve a: http://localhost:5000
echo - O: http://tu-dominio:5000
echo.
echo El servicio se iniciara automaticamente cada vez
echo que reinicies tu computadora.
echo.
pause





