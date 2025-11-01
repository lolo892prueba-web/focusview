# 🚀 FocusView - Servidor Web

## ✅ **Estado Actual:**
- **Servidor funcionando:** `http://localhost:5000`
- **IP pública:** `104.247.81.99`
- **Base de datos:** Conectada ✅

## 🌐 **Para Dominio Real:**

### **Opción 1: Dominio Gratuito (NO-IP)**
1. Ve a: https://www.noip.com
2. Crea cuenta gratuita
3. Crea hostname: `focusview.ddns.net`
4. Apunta a: `104.247.81.99`
5. Tu dominio: `http://focusview.ddns.net:5000`

### **Opción 2: Dominio Profesional**
1. Ve a: https://www.godaddy.com
2. Busca: `focusview.com`
3. Compra dominio (~$12/año)
4. Configura DNS: `@` → `104.247.81.99`
5. Tu dominio: `http://focusview.com:5000`

## 🔧 **Scripts Disponibles:**

- `INICIAR_SERVIDOR.bat` - Inicia el servidor
- `CONFIGURAR_NOIP.bat` - Configura dominio gratuito
- `CONFIGURAR_FIREWALL_AUTO.bat` - Configura firewall
- `INSTALAR_SERVICIO_24H_MEJORADO.bat` - Servicio 24/7

## 📱 **Acceso:**
- **Local:** `http://localhost:5000` ✅
- **Internet:** `http://104.247.81.99:5000` (necesita router + firewall)
- **Dominio:** `http://tu-dominio:5000` (una vez configurado)

¡Tu servidor FocusView está listo! 🎉

---

## 📦 Despliegue gratuito recomendado

Si quieres publicar la web sin coste (dominio de la plataforma) te recomiendo usar Render o Fly.io — ambos tienen planes gratuitos para apps pequeñas.

Pasos rápidos para Render (gratuito):
1. Sube tu repo a GitHub.
2. Crea una cuenta en https://render.com.
3. New → Web Service → Connect GitHub → selecciona el repo.
4. En Build Command deja vacío (Render detecta `requirements.txt`). En Start Command usa: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2` (o deja que use `Procfile`).
5. En Environment → Add Environment Variables agrega `GOOGLE_CLIENT_ID` y cualquier variable de DB.
6. Despliega: Render te dará una URL tipo `https://your-app.onrender.com` con HTTPS gratis.

Pasos rápidos para Fly.io (gratuito):
1. Instala flyctl localmente y crea cuenta: https://fly.io/docs/getting-started/
2. Desde tu repo: `fly launch` y sigue el asistente (elige región y nombre). Fly creará una app y desplegará.
3. Configura vars con `fly secrets set GOOGLE_CLIENT_ID='tu_client_id'`.
4. La app tendrá un dominio `yourapp.fly.dev` con TLS gestionado.

Notas importantes:
- Muchas plataformas gratuitas usan almacenamiento efímero: para archivos permanentes (uploads/) usa S3 o DigitalOcean Spaces.
- No subas `.env` al repo (ya añadí `.gitignore`).
- Si quieres, puedo preparar un `Dockerfile`/instrucciones adicionales o ayudarte a conectar el repo a Render/Fly.
- Si quieres, puedo preparar un `Dockerfile`/instrucciones adicionales o ayudarte a conectar el repo a Render/Fly.

## Archivos nuevos añadidos para despliegue
- `Dockerfile` — imagen lista para desplegar en Docker/PaaS.
- `.dockerignore` — no envía archivos innecesarios a la imagen.
- `deploy/focusview.service` — plantilla `systemd` para VPS.
- `deploy/focusview.nginx` — ejemplo de bloque `nginx` para proxy inverso.

### Storage S3 / Spaces / R2

El código ya soporta subir archivos a un storage compatible S3. Para DigitalOcean Spaces o Cloudflare R2 debes añadir además la variable `S3_ENDPOINT` en tus variables de entorno (por ejemplo: `https://nyc3.digitaloceanspaces.com`).

Variables que debes definir en `.env` o en la plataforma:

- `S3_BUCKET` (nombre del bucket/space)
- `S3_REGION` (opcional para Spaces; ej. `nyc3`)
- `S3_KEY` (Access Key ID)
- `S3_SECRET` (Secret Access Key)
- `S3_ENDPOINT` (opcional; necesario para DigitalOcean Spaces y Cloudflare R2)

Cuando S3 está activado, las APIs devuelven `publicUrl` (presigned URL) para cada imagen y `/api/health` mostrará `s3: true`.

## Cómo probar localmente con Docker (rápido)
1. Construir la imagen:

```powershell
docker build -t focusview:local .
```

2. Ejecutar el contenedor (exponiendo el puerto 5000):

```powershell
docker run --rm -p 5000:5000 --env-file .env focusview:local
```

La app quedará disponible en http://localhost:5000.

Si usas Windows y Docker Desktop, asegúrate de darle acceso a los archivos del disco en la configuración de Docker.





