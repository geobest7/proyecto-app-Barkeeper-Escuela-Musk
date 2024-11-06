import os  
from dotenv import load_dotenv  # Carga variables desde un archivo .env
from datetime import timedelta

# Define el directorio base como la carpeta que contiene este archivo
basedir = os.path.abspath(os.path.dirname(__file__))

# Cargar variables de entorno desde el archivo .env
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)

    # Configuración de correo electrónico
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', MAIL_USERNAME)
    
    LANGUAGES = ['en', 'es', 'it', 'ca']  # Idiomas soportados
    RECIPES_PER_PAGE = 10
    MESSAGE_PER_PAGE = 2