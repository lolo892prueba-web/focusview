# FocusView - Configuración Automática

## 🚀 Inicio Automático del Servidor Flask

### ✅ Configuración Completa Realizada

He configurado VS Code para que **automáticamente inicie el servidor Flask** cuando abras el proyecto.

### 📁 Archivos de Configuración Creados:

1. **`.vscode/tasks.json`** - Tareas automáticas de VS Code
2. **`.vscode/settings.json`** - Configuración del workspace
3. **`.vscode/launch.json`** - Configuración de depuración
4. **`.vscode/extensions.json`** - Extensiones recomendadas
5. **`FocusView.code-workspace`** - Archivo de workspace
6. **`AUTO_INICIAR_FLASK.bat`** - Script de inicio automático

### 🎯 Cómo Usar la Configuración Automática:

#### Opción 1 - Abrir con Workspace (Recomendado):
1. **Abre VS Code**
2. **File → Open Workspace from File**
3. **Selecciona:** `FocusView.code-workspace`
4. **El servidor Flask se iniciará automáticamente** ✅

#### Opción 2 - Abrir Carpeta Normal:
1. **Abre VS Code**
2. **File → Open Folder**
3. **Selecciona la carpeta del proyecto**
4. **Ejecuta:** `Ctrl+Shift+P` → `Tasks: Run Task` → `Auto Start FocusView`

#### Opción 3 - Script Manual:
1. **Ejecuta:** `AUTO_INICIAR_FLASK.bat`
2. **Se iniciará automáticamente y abrirá las páginas**

### 🔧 Funcionalidades Automáticas:

- **✅ Inicio automático del servidor Flask**
- **✅ Verificación de dependencias**
- **✅ Instalación automática de dependencias si faltan**
- **✅ Apertura automática de páginas en el puerto 5000**
- **✅ Detección si el servidor ya está ejecutándose**
- **✅ Configuración de Live Server para evitar conflictos**

### 🌐 URLs Automáticas:

Cuando se inicie automáticamente, se abrirán:
- **http://localhost:5000** - Página principal
- **http://localhost:5000/explorar** - Página de exploración
- **http://localhost:5000/login** - Página de login

### ⚙️ Configuración de VS Code:

- **Puerto Live Server:** 5001 (evita conflictos)
- **Puerto Flask:** 5000 (tu servidor principal)
- **Auto-save:** Habilitado
- **Python:** Configurado automáticamente
- **Extensiones:** Recomendadas automáticamente

### 🎉 Resultado:

**¡Ya NO necesitas ejecutar `python app.py` manualmente!**

1. **Abre VS Code con el workspace**
2. **El servidor Flask se inicia automáticamente**
3. **Las páginas se abren automáticamente en el puerto 5000**
4. **Todo funciona sin intervención manual**

### 🆘 Si Hay Problemas:

1. **Ejecuta:** `SOLUCIONAR_PROBLEMAS_VENTANAS.bat`
2. **O ejecuta:** `AUTO_INICIAR_FLASK.bat`
3. **O usa:** `ABRIR_EN_PUERTO_5000.bat`

### 💡 Consejos:

- **Usa siempre el archivo workspace** (`FocusView.code-workspace`)
- **Las extensiones se instalarán automáticamente**
- **El servidor se reinicia automáticamente si hay cambios**
- **Todo está configurado para funcionar sin configuración manual**

¡Ahora tu proyecto FocusView se iniciará automáticamente cada vez que abras VS Code! 🎉




