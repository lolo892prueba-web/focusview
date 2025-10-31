# =============================================
# CONFIGURACIÓN SEGURA - FocusView
# =============================================
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración segura para FocusView"""
    
    # Base de datos
    DB_SERVER = os.getenv('DB_SERVER', 'localhost')
    DB_DATABASE = os.getenv('DB_DATABASE', 'FocusViewDB')
    DB_USERNAME = os.getenv('DB_USERNAME', 'connection')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Jarlin88')
    DB_DRIVER = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'TU_CLIENT_ID_AQUI.apps.googleusercontent.com')
    
    # Configuración de archivos
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    @staticmethod
    def get_db_connection_string():
        """Generar string de conexión seguro"""
        return (
            f"DRIVER={Config.DB_DRIVER};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_DATABASE};"
            f"UID={Config.DB_USERNAME};"
            f"PWD={Config.DB_PASSWORD};"
            "TrustServerCertificate=yes;"
        )


