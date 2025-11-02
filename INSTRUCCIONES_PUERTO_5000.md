# FocusView - Instrucciones de Uso

## 🚀 Cómo Abrir las Páginas en el Puerto Correcto (5000)

### ✅ Método Recomendado - Usar el Script Automático

1. **Ejecuta primero el servidor Flask:**
   ```
   python app.py
   ```
   O usa el archivo: `INICIAR_SERVIDOR.bat`

2. **Abre cualquier archivo HTML directamente:**
   - Haz doble clic en `index.html`
   - Haz doble clic en `Explorar.html`
   - Haz doble clic en `login.html`

3. **El script automático te redirigirá al puerto 5000** ✅

### 🎯 Método Alternativo - Usar el Script de Apertura

1. **Ejecuta:** `ABRIR_EN_PUERTO_5000.bat`
2. **Selecciona qué página quieres abrir**
3. **Se abrirá automáticamente en el puerto 5000**

### 🔧 Solucionar Problemas de Ventanas Nuevas

Si tienes problemas con ventanas nuevas o puertos incorrectos:

1. **Ejecuta:** `SOLUCIONAR_PROBLEMAS_VENTANAS.bat`
2. **Selecciona la opción apropiada:**
   - Opción 1: Detener Live Server
   - Opción 2: Iniciar servidor Flask
   - Opción 3: Reiniciar todo
   - Opción 4: Abrir páginas directamente

### 🌐 URLs Directas (Puerto 5000)

- **Página Principal:** http://localhost:5000
- **Exploración:** http://localhost:5000/explorar  
- **Login:** http://localhost:5000/login

### ⚠️ Problemas Comunes y Soluciones

#### Si se abre en puerto 5500 o 5001:
1. **Ejecuta:** `SOLUCIONAR_PROBLEMAS_VENTANAS.bat`
2. **Selecciona opción 1** para detener Live Server
3. **O usa el script automático** que ya está configurado

#### Si hay problemas con ventanas nuevas:
1. **Ejecuta:** `SOLUCIONAR_PROBLEMAS_VENTANAS.bat`
2. **Selecciona opción 4** para abrir páginas directamente
3. **O usa:** `ABRIR_EN_PUERTO_5000.bat`

#### Si el servidor Flask no inicia:
1. **Verifica que Python esté instalado**
2. **Instala dependencias:** `pip install flask flask-cors pyodbc`
3. **Ejecuta:** `python app.py`
4. **O usa:** `SOLUCIONAR_PROBLEMAS_VENTANAS.bat` opción 2

### 🔧 Configuración de VS Code

El archivo `.vscode/settings.json` ya está configurado para:
- Usar el puerto 5001 por defecto (para evitar conflictos)
- Desactivar notificaciones de Live Server
- Redirigir automáticamente al puerto correcto
- Manejar mejor las ventanas nuevas

### 📝 Notas Importantes

- **NUNCA uses los puertos 5500 o 5001** para FocusView
- **SIEMPRE usa el puerto 5000** donde está tu servidor Flask
- **El script de redirección funciona automáticamente** en todos los archivos HTML
- **Tu servidor Flask debe estar ejecutándose** antes de abrir las páginas
- **Si hay problemas, usa el script de solución** incluido

### 🎉 ¡Listo!

Ahora puedes abrir cualquier archivo HTML y automáticamente se redirigirá al puerto 5000 donde está tu servidor Flask funcionando correctamente.

### 🆘 Si Todo Falla

1. **Ejecuta:** `SOLUCIONAR_PROBLEMAS_VENTANAS.bat`
2. **Selecciona opción 3** (Reiniciar todo)
3. **Esto detendrá Live Server y iniciará Flask automáticamente**
