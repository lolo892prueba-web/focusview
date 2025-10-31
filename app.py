# =============================================
# SERVIDOR FOCUSVIEW - FLASK + PYTHON
# Conecta index.html con SQL Server
# =============================================

from flask import Flask, request, jsonify, send_from_directory, send_file, session
from flask_cors import CORS
import pyodbc
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import json
from config import Config
import requests
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import timedelta

# Optional S3 support
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    S3_AVAILABLE = True
except Exception:
    S3_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend
# Usar SECRET_KEY de Config para sesiones seguras
app.secret_key = Config.SECRET_KEY

# =============================================
# CONFIGURACIÓN
# =============================================

# Carpeta para subir imágenes
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear carpeta uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configurar S3 si está disponible mediante variables de entorno
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
S3_ACCESS_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET')
S3_ENDPOINT = os.getenv('S3_ENDPOINT')

# Safe mode: allow running without a database or external services
DISABLE_DB = os.getenv('DISABLE_DB', '0').lower() in ('1', 'true', 'yes')

if S3_AVAILABLE and S3_BUCKET and S3_ACCESS_KEY and S3_SECRET:
    try:
        # Build params dynamically so endpoint_url is optional (for Spaces/R2)
        s3_params = {
            'aws_access_key_id': S3_ACCESS_KEY,
            'aws_secret_access_key': S3_SECRET
        }
        if S3_REGION:
            s3_params['region_name'] = S3_REGION
        if S3_ENDPOINT:
            s3_params['endpoint_url'] = S3_ENDPOINT

        s3_client = boto3.client('s3', **s3_params)
        print('✅ S3 client configurado (uploads a S3 habilitado)')
        USE_S3 = True
    except Exception as e:
        print(f'⚠️ No se pudo configurar S3: {e}')
        USE_S3 = False
else:
    USE_S3 = False

# =============================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================

# Configuración de base de datos para producción
import os

DB_CONFIG = {
    'server': Config.DB_SERVER,
    'database': Config.DB_DATABASE,
    'username': Config.DB_USERNAME,
    # No incluimos la contraseña en los logs; se lee desde Config
    'driver': Config.DB_DRIVER
}

def get_db_connection():
    """Crear conexión a la base de datos usando `config.Config`.

    Mejor manejo de errores y salida segura de mensajes.
    """
    if DISABLE_DB:
        raise RuntimeError('Database access disabled by DISABLE_DB environment variable')

    try:
        conn_str = Config.get_db_connection_string()
        conn = pyodbc.connect(conn_str)
        print('✅ Conectado a la base de datos')
        return conn
    except pyodbc.Error as e:
        # Evitar índices fuera de rango en e.args y mostrar representación completa
        args_str = ', '.join(map(str, e.args)) if getattr(e, 'args', None) else str(e)
        print(f'❌ Error de base de datos: {e!r}')
        print(f'   Detalles: {args_str}')
        raise
    except Exception as e:
        print(f'❌ Error inesperado al conectar: {e!r}')
        print(f'   Tipo de error: {type(e).__name__}')
        raise


# ----------------------
# Helpers para usar la base de datos SQL Server para usuarios
# ----------------------
def ensure_users_tables():
    """Crear tablas Users y PasswordResets si no existen (seguro para SQL Server)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Users]') AND type in (N'U'))
        BEGIN
            CREATE TABLE dbo.Users (
                Id INT IDENTITY(1,1) PRIMARY KEY,
                Email NVARCHAR(255) UNIQUE NOT NULL,
                Name NVARCHAR(255) NULL,
                PasswordHash NVARCHAR(255) NULL,
                GoogleSub NVARCHAR(255) NULL,
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        END

        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[PasswordResets]') AND type in (N'U'))
        BEGIN
            CREATE TABLE dbo.PasswordResets (
                Token NVARCHAR(255) PRIMARY KEY,
                UserId INT,
                ExpiresAt DATETIME,
                CONSTRAINT FK_PasswordResets_Users FOREIGN KEY (UserId) REFERENCES dbo.Users(Id)
            )
        END
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print('✅ Tablas Users y PasswordResets aseguradas en SQL Server')
    except Exception as e:
        print(f'⚠️ No se pudo asegurar tablas de usuarios: {e}')


def sql_find_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Email, Name, PasswordHash, GoogleSub, CreatedAt FROM dbo.Users WHERE Email = ?", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def sql_find_user_by_google_sub(google_sub):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Email, Name, PasswordHash, GoogleSub, CreatedAt FROM dbo.Users WHERE GoogleSub = ?", (google_sub,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def sql_create_user(email, name=None, password_hash=None, google_sub=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ejecutar INSERT como una operación separada. Algunos drivers/entornos no
    # permiten mezclar múltiples statements en una sola llamada a execute().
    cursor.execute(
        "INSERT INTO dbo.Users (Email, Name, PasswordHash, GoogleSub, CreatedAt) VALUES (?, ?, ?, ?, GETDATE())",
        (email, name, password_hash, google_sub)
    )
    conn.commit()

    # Intentar usar OUTPUT INSERTED.Id — más fiable con pyodbc/ODBC drivers
    try:
        # Re-ejecutar el INSERT usando OUTPUT para obtener el id en la misma llamada
        cursor.execute(
            "INSERT INTO dbo.Users (Email, Name, PasswordHash, GoogleSub, CreatedAt) OUTPUT INSERTED.Id VALUES (?, ?, ?, ?, GETDATE())",
            (email, name, password_hash, google_sub)
        )
        row = cursor.fetchone()
        new_id = int(row[0]) if row and row[0] is not None else None
        conn.commit()
    except Exception as e:
        # Si OUTPUT no funciona, intentar la estrategia SCOPE_IDENTITY() separada
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            cursor.execute(
                "INSERT INTO dbo.Users (Email, Name, PasswordHash, GoogleSub, CreatedAt) VALUES (?, ?, ?, ?, GETDATE())",
                (email, name, password_hash, google_sub)
            )
            conn.commit()
            cursor.execute("SELECT SCOPE_IDENTITY() AS NewId")
            row = cursor.fetchone()
            new_id = int(row[0]) if row and row[0] is not None else None
        except Exception:
            cursor.close()
            conn.close()
            raise

    cursor.close()
    conn.close()
    if new_id is None:
        raise RuntimeError('No se pudo obtener el Id del usuario insertado')
    return new_id


def sql_update_password(user_id, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE dbo.Users SET PasswordHash = ? WHERE Id = ?", (password_hash, user_id))
    conn.commit()
    cursor.close()
    conn.close()


def sql_link_google_sub(user_id, google_sub):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE dbo.Users SET GoogleSub = ? WHERE Id = ?", (google_sub, user_id))
    conn.commit()
    cursor.close()
    conn.close()


def sql_create_password_reset(user_id, token, expires_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dbo.PasswordResets (Token, UserId, ExpiresAt) VALUES (?, ?, ?)", (token, user_id, expires_at))
    conn.commit()
    cursor.close()
    conn.close()


def sql_get_password_reset(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Token, UserId, ExpiresAt FROM dbo.PasswordResets WHERE Token = ?", (token,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def sql_delete_password_reset(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.PasswordResets WHERE Token = ?", (token,))
    conn.commit()
    cursor.close()
    conn.close()


# ----------------------
# SQL Server helpers para comentarios y notificaciones
# ----------------------
def sql_get_publication_owner(publicacion_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UsuarioID FROM Publicaciones WHERE PublicacionID = ?", (publicacion_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def sql_create_comment(user_id, publicacion_id, comment):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Comentarios (UsuarioID, PublicacionID, Comentario, FechaComentario) VALUES (?, ?, ?, GETDATE())", (user_id, publicacion_id, comment))
    conn.commit()
    cursor.close()
    conn.close()


def sql_create_notification(user_id, tipo, mensaje, publicacion_id=None, origin_user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Notificaciones (UsuarioID, TipoNotificacion, Mensaje, PublicacionID, UsuarioOrigenID, Leida, FechaNotificacion) VALUES (?, ?, ?, ?, ?, 0, GETDATE())", (user_id, tipo, mensaje, publicacion_id, origin_user_id))
    conn.commit()
    cursor.close()
    conn.close()


def sql_get_notifications_for_user(user_id, limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT NotificacionID, TipoNotificacion, Mensaje, PublicacionID, UsuarioOrigenID, Leida, FechaNotificacion FROM Notificaciones WHERE UsuarioID = ? ORDER BY FechaNotificacion DESC", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def sql_mark_notification_read(notification_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Notificaciones SET Leida = 1 WHERE NotificacionID = ?", (notification_id,))
    conn.commit()
    cursor.close()
    conn.close()


# Asegurar tablas al iniciar la aplicación (si la BD está disponible)
try:
    if not DISABLE_DB:
        ensure_users_tables()
except Exception as e:
    print(f'⚠️ Error asegurando tablas de usuarios al iniciar: {e}')


# ----------------------
# SQLite local para usuarios y resets (modo desarrollo)
# ----------------------
SQLITE_FILE = os.path.join(os.path.dirname(__file__), 'local_users.db')

def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        password_hash TEXT,
        google_sub TEXT,
        created_at TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS password_resets (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        expires_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        publicacion_id INTEGER,
        comment TEXT,
        created_at TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        message TEXT,
        publicacion_id INTEGER,
        origin_user_id INTEGER,
        read INTEGER DEFAULT 0,
        created_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Inicializar DB local si no existe
try:
    init_sqlite()
    print('✅ SQLite local para usuarios inicializada')
except Exception as e:
    print(f'⚠️ No se pudo inicializar SQLite local: {e}')

# ----------------------
# Wrappers que usan SQL Server cuando está disponible, o SQLite como fallback
# ----------------------
def find_user_by_email(email):
    """Intentar obtener usuario desde SQL Server; si falla, usar SQLite local."""
    if not email:
        return None
    # Intentar SQL Server si no está deshabilitada
    if not DISABLE_DB:
        try:
            row = sql_find_user_by_email(email)
            if row:
                return row
        except Exception as e:
            print(f"[WARN] sql_find_user_by_email falló, usando SQLite: {e}")

    # Fallback a SQLite
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('SELECT id, email, name, password_hash, google_sub, created_at FROM users WHERE email = ?', (email,))
        r = cur.fetchone()
        cur.close()
        conn.close()
        return r
    except Exception as e:
        print(f"[ERROR] sqlite lookup failed: {e}")
        return None


def find_user_by_google_sub(google_sub):
    if not google_sub:
        return None
    if not DISABLE_DB:
        try:
            row = sql_find_user_by_google_sub(google_sub)
            if row:
                return row
        except Exception as e:
            print(f"[WARN] sql_find_user_by_google_sub falló, usando SQLite: {e}")

    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('SELECT id, email, name, password_hash, google_sub, created_at FROM users WHERE google_sub = ?', (google_sub,))
        r = cur.fetchone()
        cur.close()
        conn.close()
        return r
    except Exception as e:
        print(f"[ERROR] sqlite lookup by google_sub failed: {e}")
        return None


def create_user(email, name=None, password_hash=None, google_sub=None):
    # Intentar SQL Server primero
    if not DISABLE_DB:
        try:
            return sql_create_user(email=email, name=name, password_hash=password_hash, google_sub=google_sub)
        except Exception as e:
            print(f"[WARN] sql_create_user falló, intentando SQLite: {e}")

    # SQLite fallback
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('INSERT INTO users (email, name, password_hash, google_sub, created_at) VALUES (?, ?, ?, ?, ?)', (email, name, password_hash, google_sub, now))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"[ERROR] sqlite create_user failed: {e}")
        raise


def update_password(user_id, password_hash):
    if not DISABLE_DB:
        try:
            return sql_update_password(user_id, password_hash)
        except Exception as e:
            print(f"[WARN] sql_update_password falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] sqlite update_password failed: {e}")
        raise


def link_google_sub(user_id, google_sub):
    if not DISABLE_DB:
        try:
            return sql_link_google_sub(user_id, google_sub)
        except Exception as e:
            print(f"[WARN] sql_link_google_sub falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('UPDATE users SET google_sub = ? WHERE id = ?', (google_sub, user_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] sqlite link_google_sub failed: {e}")
        raise


def create_password_reset(user_id, token, expires_at):
    if not DISABLE_DB:
        try:
            return sql_create_password_reset(user_id, token, expires_at)
        except Exception as e:
            print(f"[WARN] sql_create_password_reset falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('INSERT INTO password_resets (token, user_id, expires_at) VALUES (?, ?, ?)', (token, user_id, expires_at))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] sqlite create_password_reset failed: {e}")
        raise


def get_password_reset(token):
    if not DISABLE_DB:
        try:
            return sql_get_password_reset(token)
        except Exception as e:
            print(f"[WARN] sql_get_password_reset falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('SELECT token, user_id, expires_at FROM password_resets WHERE token = ?', (token,))
        r = cur.fetchone()
        cur.close()
        conn.close()
        return r
    except Exception as e:
        print(f"[ERROR] sqlite get_password_reset failed: {e}")
        return None


def delete_password_reset(token):
    if not DISABLE_DB:
        try:
            return sql_delete_password_reset(token)
        except Exception as e:
            print(f"[WARN] sql_delete_password_reset falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM password_resets WHERE token = ?', (token,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] sqlite delete_password_reset failed: {e}")
        raise


# Wrappers para comentarios y notificaciones (SQL Server -> SQLite fallback)
def get_publication_owner(publicacion_id):
    if not publicacion_id:
        return None
    if not DISABLE_DB:
        try:
            owner = sql_get_publication_owner(publicacion_id)
            if owner:
                return owner
        except Exception as e:
            print(f"[WARN] sql_get_publication_owner falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM comments WHERE publicacion_id = ? LIMIT 1', (publicacion_id,))
        r = cur.fetchone()
        cur.close()
        conn.close()
        # Nota: en SQLite local no almacenamos owner de publicaciones; devolver None
        return None
    except Exception as e:
        print(f"[ERROR] sqlite get_publication_owner failed: {e}")
        return None


def create_comment(user_id, publicacion_id, comment):
    # Intentar SQL Server
    if not DISABLE_DB:
        try:
            return sql_create_comment(user_id, publicacion_id, comment)
        except Exception as e:
            print(f"[WARN] sql_create_comment falló, usando SQLite: {e}")
    # SQLite fallback
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('INSERT INTO comments (user_id, publicacion_id, comment, created_at) VALUES (?, ?, ?, ?)', (user_id, publicacion_id, comment, now))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"[ERROR] sqlite create_comment failed: {e}")
        raise


def create_notification(user_id, tipo, mensaje, publicacion_id=None, origin_user_id=None):
    if not DISABLE_DB:
        try:
            return sql_create_notification(user_id, tipo, mensaje, publicacion_id, origin_user_id)
        except Exception as e:
            print(f"[WARN] sql_create_notification falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('INSERT INTO notifications (user_id, type, message, publicacion_id, origin_user_id, read, created_at) VALUES (?, ?, ?, ?, ?, 0, ?)', (user_id, tipo, mensaje, publicacion_id, origin_user_id, now))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] sqlite create_notification failed: {e}")
        raise


def get_notifications_for_user(user_id, limit=50):
    if not user_id:
        return []
    if not DISABLE_DB:
        try:
            rows = sql_get_notifications_for_user(user_id, limit=limit)
            # mapear rows a dict
            results = []
            for r in rows:
                results.append({
                    'id': int(r[0]),
                    'type': r[1],
                    'message': r[2],
                    'publicacion_id': r[3],
                    'origin_user_id': r[4],
                    'read': bool(r[5]),
                    'created_at': str(r[6])
                })
            return results
        except Exception as e:
            print(f"[WARN] sql_get_notifications_for_user falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('SELECT id, type, message, publicacion_id, origin_user_id, read, created_at FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        results = []
        for r in rows:
            results.append({'id': r[0], 'type': r[1], 'message': r[2], 'publicacion_id': r[3], 'origin_user_id': r[4], 'read': bool(r[5]), 'created_at': r[6]})
        return results
    except Exception as e:
        print(f"[ERROR] sqlite get_notifications_for_user failed: {e}")
        return []


def mark_notification_read(notification_id):
    if not notification_id:
        return
    if not DISABLE_DB:
        try:
            return sql_mark_notification_read(notification_id)
        except Exception as e:
            print(f"[WARN] sql_mark_notification_read falló, usando SQLite: {e}")
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute('UPDATE notifications SET read = 1 WHERE id = ?', (notification_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] sqlite mark_notification_read failed: {e}")
        raise

def allowed_file(filename):
    """Verificar si el archivo es permitido con validación mejorada"""
    if not filename or '.' not in filename:
        return False
    
    # Obtener extensión
    extension = filename.rsplit('.', 1)[1].lower()
    
    # Verificar extensión permitida
    if extension not in ALLOWED_EXTENSIONS:
        return False
    
    # Verificar que el nombre del archivo no contenga caracteres peligrosos
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        if char in filename:
            return False
    
    # Verificar longitud del nombre
    if len(filename) > 255:
        return False
    
    return True

# =============================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
# =============================================

# Configurar carpeta de archivos estáticos
app.static_folder = '.'
app.static_url_path = ''

# =============================================
# RUTAS PARA SERVIR ARCHIVOS HTML
# =============================================

@app.route('/')
def index():
    """Servir index.html"""
    return send_file('index.html')

@app.route('/index.html')
def index_html():
    """Servir index.html directamente"""
    return send_file('index.html')

@app.route('/index')
def index_route():
    """Ruta alternativa para index"""
    return send_file('index.html')

@app.route('/login')
def login():
    """Servir login.html"""
    return send_file('login.html')

@app.route('/login.html')
def login_html():
    """Servir login.html directamente"""
    return send_file('login.html')

@app.route('/explorar')
def explorar():
    """Servir Explorar.html"""
    return send_file('Explorar.html')

@app.route('/Explorar.html')
def explorar_html():
    """Servir Explorar.html directamente"""
    return send_file('Explorar.html')

# =============================================
# RUTAS PARA ARCHIVOS ESTÁTICOS
# =============================================

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir imágenes subidas"""
    if USE_S3:
        # Redirigir a la URL pública de S3 (asumiendo bucket público o uso de presigned URL)
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': filename},
                ExpiresIn=3600
            )
            return jsonify({'success': True, 'url': url})
        except Exception as e:
            print(f'⚠️ Error generando URL S3: {e}')
            return "Archivo no encontrado", 404
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    """Descargar imágenes"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return "Archivo no encontrado", 404

@app.route('/favicon.ico')
def favicon():
    """Servir favicon"""
    return send_file('imagen_circular_recortada (1).png')

@app.route('/<path:filename>')
def serve_static(filename):
    """Servir archivos estáticos (CSS, JS, imágenes, etc.)"""
    # Lista de extensiones de archivos estáticos
    static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.html']
    
    # Verificar si es un archivo estático
    if any(filename.lower().endswith(ext) for ext in static_extensions):
        try:
            return send_from_directory('.', filename)
        except FileNotFoundError:
            return "Archivo no encontrado", 404
    
    # Si no es un archivo estático, devolver 404
    return "Archivo no encontrado", 404

# =============================================
# API - OBTENER GALERÍA
# =============================================

@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    """Obtener todas las imágenes para la galería"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ejecutar procedimiento almacenado
        cursor.execute("""
            EXEC sp_GetPublicacionesPorCategoria 
                @CategoriaID = NULL,
                @PageNumber = 1,
                @PageSize = 50
        """)
        
        # Obtener resultados
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            # Si S3 está activado y la columna ImagenURL tiene el prefijo /uploads/, generar URL pública
            try:
                if USE_S3 and row_dict.get('ImagenURL') and row_dict.get('ImagenURL').startswith('/uploads/'):
                    key = row_dict.get('ImagenURL').replace('/uploads/', '')
                    try:
                        presigned = s3_client.generate_presigned_url(
                            'get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=3600
                        )
                        row_dict['publicUrl'] = presigned
                    except Exception as e:
                        print(f'⚠️ Error generando presigned para galería: {e}')
                        row_dict['publicUrl'] = None
            except Exception:
                row_dict['publicUrl'] = None

            results.append(row_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'images': results
        })
        
    except Exception as e:
        print(f'❌ Error al obtener galería: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================
# API - SUBIR IMAGEN
# =============================================

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Subir imagen a la base de datos"""
    try:
        # Verificar que se envió un archivo
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se seleccionó ninguna imagen'
            }), 400
        
        file = request.files['image']
        
        # Verificar que el archivo tiene nombre
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó ninguna imagen'
            }), 400
        
        # Verificar que el archivo es permitido
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Solo se permiten imágenes JPG, PNG o GIF'
            }), 400
        
        # Obtener datos del formulario
        titulo = request.form.get('titulo', 'Mi Nueva Imagen')
        descripcion = request.form.get('descripcion', '')
        categoria_id = request.form.get('categoriaID', 1)
        usuario_id = request.form.get('usuarioID', 1)
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(filepath)
        
        # Guardar en base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imagen_url = f"/uploads/{unique_filename}"

        # Si está configurado S3, subir el archivo y eliminar copia local
        if USE_S3:
            try:
                s3_key = unique_filename
                s3_client.upload_file(filepath, S3_BUCKET, s3_key)
                # Eliminar copia local si se subió a S3
                try:
                    os.remove(filepath)
                except Exception:
                    pass
                # Usar la key (nombre) en ImagenURL y el path público se gestionará por S3
                imagen_url = f"/uploads/{s3_key}"
            except (BotoCoreError, ClientError) as e:
                print(f'⚠️ Error subiendo a S3: {e}')
                # Seguir con la versión local como fallback
        
        cursor.execute("""
            EXEC sp_CrearPublicacion
                @UsuarioID = ?,
                @Titulo = ?,
                @Descripcion = ?,
                @ImagenURL = ?,
                @ImagenNombre = ?,
                @ImagenTamaño = ?,
                @CategoriaID = ?
        """, (usuario_id, titulo, descripcion, imagen_url, filename, file_size, categoria_id))
        
        # Obtener ID de la nueva publicación
        cursor.execute("SELECT @@IDENTITY AS NuevaPublicacionID")
        nueva_publicacion_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f'✅ Imagen subida exitosamente: {titulo} (ID: {nueva_publicacion_id})')
        
        response_payload = {
            'success': True,
            'message': 'Imagen subida exitosamente',
            'publicacionID': int(nueva_publicacion_id),
            'imagenURL': imagen_url,
            'titulo': titulo
        }

        # Si usamos S3, generar una URL presignada para acceso directo desde el frontend
        if USE_S3:
            try:
                presigned = s3_client.generate_presigned_url(
                    'get_object', Params={'Bucket': S3_BUCKET, 'Key': unique_filename}, ExpiresIn=3600
                )
                response_payload['publicUrl'] = presigned
            except Exception as e:
                print(f'⚠️ Error generando presigned en upload: {e}')

        return jsonify(response_payload)
        
    except Exception as e:
        print(f'❌ Error al subir imagen: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================
# API - DAR LIKE
# =============================================

@app.route('/api/like', methods=['POST'])
def dar_like():
    """Dar o quitar like a una publicación"""
    try:
        data = request.get_json()
        publicacion_id = data.get('publicacionID')
        usuario_id = data.get('usuarioID', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ejecutar procedimiento almacenado
        cursor.execute("""
            EXEC sp_DarLike
                @UsuarioID = ?,
                @PublicacionID = ?
        """, (usuario_id, publicacion_id))
        
        # Obtener resultado
        resultado = cursor.fetchone()[0]
        
        # Obtener nuevo contador de likes
        cursor.execute("""
            SELECT Likes FROM Publicaciones 
            WHERE PublicacionID = ?
        """, (publicacion_id,))
        
        new_like_count = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': resultado,
            'newLikeCount': new_like_count
        })
        
    except Exception as e:
        print(f'❌ Error al procesar like: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================
# API - ELIMINAR PUBLICACIÓN
# =============================================

@app.route('/api/delete/<int:publicacion_id>', methods=['DELETE'])
def delete_publicacion(publicacion_id):
    """Eliminar una publicación de la base de datos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener información de la imagen antes de borrar
        cursor.execute("SELECT ImagenURL FROM Publicaciones WHERE PublicacionID = ?", (publicacion_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Publicación no encontrada'})
        
        # Eliminar de la base de datos
        cursor.execute("DELETE FROM Publicaciones WHERE PublicacionID = ?", (publicacion_id,))
        conn.commit()
        
        # Intentar eliminar el archivo físico
        try:
            image_path = result[0]
            if image_path and image_path.startswith('/uploads/'):
                # Remover el prefijo /uploads/ para obtener el nombre del archivo
                filename = image_path.replace('/uploads/', '')
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f'✅ Archivo eliminado: {full_path}')
        except Exception as file_error:
            print(f'⚠️ Error al eliminar archivo: {file_error}')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Publicación eliminada exitosamente'
        })
        
    except Exception as e:
        print(f'❌ Error al eliminar publicación: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================
# API - OBTENER CATEGORÍAS
# =============================================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Obtener todas las categorías"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM Categorias 
            WHERE Activa = 1 
            ORDER BY Nombre
        """)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            try:
                if USE_S3 and row_dict.get('ImagenURL') and row_dict.get('ImagenURL').startswith('/uploads/'):
                    key = row_dict.get('ImagenURL').replace('/uploads/', '')
                    try:
                        presigned = s3_client.generate_presigned_url(
                            'get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=3600
                        )
                        row_dict['publicUrl'] = presigned
                    except Exception as e:
                        print(f'⚠️ Error generando presigned para explore: {e}')
                        row_dict['publicUrl'] = None
            except Exception:
                row_dict['publicUrl'] = None

            results.append(row_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'categories': results
        })
        
    except Exception as e:
        print(f'❌ Error al obtener categorías: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================
# API - EXPLORAR POR CATEGORÍA
# =============================================

@app.route('/api/explore/<categoria>', methods=['GET'])
def explore_category(categoria):
    """Obtener imágenes por categoría"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # Mapear nombres de categorías a IDs
        categoria_map = {
            'all': None,
            'paisajes': 1,
            'animales': 2,
            'arte': 3,
            'comida': 4,
            'arquitectura': 5,
            'moda': 6,
            'viajes': 7,
            'musica': 8,
            'tecnologia': 9,
            'fotografia': 10,
            'naturaleza': 11,
            'deporte': 12
        }
        
        categoria_id = categoria_map.get(categoria.lower())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            EXEC sp_GetPublicacionesPorCategoria
                @CategoriaID = ?,
                @PageNumber = ?,
                @PageSize = ?
        """, (categoria_id, page, limit))
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'images': results,
            'categoria': categoria
        })
        
    except Exception as e:
        print(f'❌ Error al explorar categoría: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================
# RUTA DE PRUEBA
# =============================================

@app.route('/api/test', methods=['GET'])
def test():
    """Probar que el servidor está funcionando"""
    return jsonify({
        'success': True,
        'message': '¡Servidor Flask funcionando correctamente!',
        'database': DB_CONFIG['database'],
        'server': DB_CONFIG['server']
    })


@app.route('/api/comment', methods=['POST'])
def api_comment():
    try:
        user = session.get('user')
        if not user:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        data = request.get_json() or {}
        publicacion_id = data.get('publicacionID')
        comment = (data.get('comment') or '').strip()
        if not publicacion_id or not comment:
            return jsonify({'success': False, 'error': 'publicacionID y comment requeridos'}), 400

        user_id = int(user.get('id'))
        # Crear comentario
        new_id = create_comment(user_id, publicacion_id, comment)

        # Intentar notificar al propietario de la publicación
        try:
            owner = get_publication_owner(publicacion_id)
            if owner and int(owner) != user_id:
                mensaje = f"{user.get('name','Usuario')} comentó: {comment[:120]}"
                create_notification(owner, 'comentario', mensaje, publicacion_id=publicacion_id, origin_user_id=user_id)
        except Exception as e:
            print(f"[WARN] No se pudo crear notificación por comentario: {e}")

        return jsonify({'success': True, 'commentId': new_id})
    except Exception as e:
        print(f'❌ Error en /api/comment: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notifications', methods=['GET'])
def api_notifications():
    try:
        user = session.get('user')
        if not user:
            return jsonify({'success': False, 'notifications': []})
        user_id = int(user.get('id'))
        notis = get_notifications_for_user(user_id)
        return jsonify({'success': True, 'notifications': notis})
    except Exception as e:
        print(f'❌ Error en /api/notifications: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notifications/mark-read', methods=['POST'])
def api_notifications_mark_read():
    try:
        user = session.get('user')
        if not user:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        data = request.get_json() or {}
        nid = data.get('notificationId')
        if not nid:
            return jsonify({'success': False, 'error': 'notificationId requerido'}), 400
        mark_notification_read(nid)
        return jsonify({'success': True})
    except Exception as e:
        print(f'❌ Error en /api/notifications/mark-read: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check para plataformas de despliegue y monitorización"""
    # Chequeo básico: respuesta OK y flag de S3
    return jsonify({
        'success': True,
        'status': 'ok',
        's3': USE_S3
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Endpoint público mínimo para exponer configuraciones necesarias
    en el frontend (por ejemplo Google Client ID). No incluye secretos.
    """
    try:
        return jsonify({
            'success': True,
            'googleClientId': Config.GOOGLE_CLIENT_ID,
            's3Enabled': USE_S3,
            's3Bucket': S3_BUCKET if USE_S3 else None
        })
    except Exception as e:
        print(f'❌ Error en /api/config: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/google', methods=['POST'])
def auth_google():
    """Verificar token de Google recibido desde el frontend y crear sesión.

    Este endpoint usa el endpoint público de Google TokenInfo para validar el id_token
    y verifica que el `aud` coincida con el `GOOGLE_CLIENT_ID` configurado.
    """
    try:
        data = request.get_json() or {}
        token = data.get('credential')
        if not token:
            return jsonify({'success': False, 'error': 'Falta el token'}), 400

        # Modo demo/local: aceptar token especial para pruebas sin llamar a Google
        # Permitir desde localhost para facilitar testing sin cambiar env vars
        client_ip = request.remote_addr or ''
        host_header = (request.host or '').lower()
        print(f"[DEBUG] /api/auth/google called - token={token!r} host={host_header!r} ip={client_ip!r}")
        # permitir demo si viene de localhost (por IP o por Host header)
        if token in ('DEMO', 'MOCK') and (
            client_ip.startswith('127.0') or client_ip == '::1' or 'localhost' in host_header
        ):
            user = {
                'email': 'demo@focusview.local',
                'name': 'Usuario Demo',
                'picture': 'https://ui-avatars.com/api/?name=Demo+User&background=4285F4&color=fff',
                'sub': 'demo-sub-12345'
            }
            session['user'] = user
            return jsonify({'success': True, 'user': user})

        # Llamar al endpoint oficial de Google para validar el id_token
        resp = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': token}, timeout=5)
        if resp.status_code != 200:
            return jsonify({'success': False, 'error': 'Token inválido'}), 401

        info = resp.json()

        # Verificar audiencia
        if info.get('aud') != Config.GOOGLE_CLIENT_ID:
            return jsonify({'success': False, 'error': 'Audience inválida'}), 401

        # Integración con la base de datos: buscar por GoogleSub o por email
        google_sub = info.get('sub')
        email = info.get('email')
        name = info.get('name')

        # 1) Buscar usuario por GoogleSub
        db_user = None
        try:
            db_row = find_user_by_google_sub(google_sub)
            if db_row:
                db_user = db_row
        except Exception as e:
            print(f'⚠️ Error buscando usuario por google_sub: {e}')

        # 2) Si no existe, buscar por email
        if not db_user and email:
            try:
                db_row = find_user_by_email(email)
                if db_row:
                    db_user = db_row
                    # vincular google_sub si no estaba
                    try:
                        # en filas de SQL Server GoogleSub está en índice 4; en SQLite también usamos esa columna
                        if not db_row[4]:
                            link_google_sub(db_row[0], google_sub)
                    except Exception as e:
                        print(f'⚠️ Error vinculando google_sub: {e}')
            except Exception as e:
                print(f'⚠️ Error buscando usuario por email: {e}')

        # 3) Si no existe, crear usuario nuevo con google_sub
        if not db_user:
            try:
                new_id = create_user(email=email, name=name, password_hash=None, google_sub=google_sub)
                db_user = find_user_by_email(email)
            except Exception as e:
                print(f'❌ Error creando usuario desde Google: {e}')
                return jsonify({'success': False, 'error': 'No se pudo crear usuario'}), 500

        # Construir objeto usuario público
        user = {
            'id': int(db_user[0]),
            'email': db_user[1],
            'name': db_user[2],
            'google_sub': db_user[4]
        }
        session['user'] = user

        return jsonify({'success': True, 'user': user})

    except Exception as e:
        print(f'❌ Error en /api/auth/google: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================
# MANEJO DE ERRORES
# =============================================

@app.errorhandler(404)
def not_found(error):
    """Manejo simple de 404: devolver JSON limpio."""
    return jsonify({'success': False, 'error': 'Ruta no encontrada'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Manejo simple de 500: devolver JSON limpio."""
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500


@app.route('/api/session', methods=['GET'])
def get_session():
    """Devolver información mínima de la sesión si el usuario está autenticado."""
    user = session.get('user')
    if user:
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': True, 'user': None})


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})


@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        name = data.get('name')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email y contraseña requeridos'}), 400

        # Debug: traza para entender fallos en entorno local
        print(f"[DEBUG] api_register inicio - email={email!r} name={name!r}")

        # Verificar existencia
        try:
            existing = find_user_by_email(email)
        except Exception as e:
            print(f"[DEBUG] error al buscar usuario por email: {e!r}")
            raise

        if existing:
            print(f"[DEBUG] usuario ya existe: {email}")
            return jsonify({'success': False, 'error': 'El correo ya está registrado'}), 409

        password_hash = generate_password_hash(password)

        try:
            print("[DEBUG] intentando crear usuario en la BD...")
            new_id = create_user(email=email, name=name, password_hash=password_hash, google_sub=None)
            print(f"[DEBUG] usuario creado con id={new_id}")
        except Exception as e:
            print(f"[DEBUG] error creando usuario: {e!r}")
            raise

        return jsonify({'success': True, 'userId': new_id})
    except Exception as e:
        print(f'❌ Error en /api/register: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email y contraseña requeridos'}), 400
        row = find_user_by_email(email)
        if not row:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        stored_hash = row[3]
        if not stored_hash:
            return jsonify({'success': False, 'error': 'Usuario registrado sin contraseña. Usa Google Sign-In.'}), 400

        if not check_password_hash(stored_hash, password):
            return jsonify({'success': False, 'error': 'Contraseña incorrecta'}), 401

        user = {'id': int(row[0]), 'email': row[1], 'name': row[2]}
        session['user'] = user
        return jsonify({'success': True, 'user': user})
    except Exception as e:
        print(f'❌ Error en /api/auth/login: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({'success': False, 'error': 'Email requerido'}), 400

        row = find_user_by_email(email)
        if not row:
            # No revelar existencia del correo
            return jsonify({'success': True, 'message': 'Si el correo existe, recibirás instrucciones.'})

        user_id = int(row[0])
        token = secrets.token_urlsafe(48)
        expires_at = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        create_password_reset(user_id, token, expires_at)

        # En desarrollo devolvemos la URL de reset para probar. En producción enviar por email.
        reset_url = f"http://localhost:5000/reset.html?token={token}"
        print(f'🔒 Reset URL (dev): {reset_url}')
        return jsonify({'success': True, 'resetUrl': reset_url})
    except Exception as e:
        print(f'❌ Error en /api/forgot-password: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    try:
        data = request.get_json() or {}
        token = data.get('token')
        new_password = data.get('password')
        if not token or not new_password:
            return jsonify({'success': False, 'error': 'Token y nueva contraseña requeridos'}), 400

        row = get_password_reset(token)
        if not row:
            return jsonify({'success': False, 'error': 'Token inválido o expirado'}), 400

        expires_at = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
        if datetime.utcnow() > expires_at:
            delete_password_reset(token)
            return jsonify({'success': False, 'error': 'Token expirado'}), 400

        user_id = int(row[1])
        password_hash = generate_password_hash(new_password)
        update_password(user_id, password_hash)
        delete_password_reset(token)
        return jsonify({'success': True})
    except Exception as e:
        print(f'❌ Error en /api/reset-password: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print('═══════════════════════════════════════════════════════════════')
    print('  🚀 SERVIDOR FOCUSVIEW - FLASK + PYTHON')
    print('═══════════════════════════════════════════════════════════════')
    print(f'📱 Servidor: http://localhost:5000')
    try:
        db_info = f"{DB_CONFIG.get('server')}/{DB_CONFIG.get('database')}"
    except Exception:
        db_info = 'Desconocido'
    print(f'🗄️  Base de datos: {db_info}')
    print('═══════════════════════════════════════════════════════════════\n')

    # Probar conexión a base de datos al iniciar (si no está deshabilitada)
    if not DISABLE_DB:
        try:
            conn = get_db_connection()
            conn.close()
            print('✅ Conexión a base de datos exitosa\n')
        except Exception as e:
            print(f'❌ Error al conectar a base de datos: {e}\n')
            print('⚠️  El servidor iniciará pero las funciones de BD no funcionarán\n')
    else:
        print('⚠️ DISABLE_DB activado: iniciando en modo seguro (sin acceso a BD)\n')

    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
