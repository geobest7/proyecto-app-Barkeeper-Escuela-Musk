import os  
from dotenv import load_dotenv  # Importa la función para cargar variables de entorno desde un archivo .env
from datetime import timedelta  # Asegúrate de importar timedelta para configurar la expiración de la sesión

# Define el directorio base como la carpeta que contiene este archivo
basedir = os.path.abspath(os.path.dirname(__file__))

# Carga las variables de entorno desde el archivo .env en el directorio base
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    # Obtiene la clave secreta de las variables de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key'
    
    # Configura la URI de la base de datos
    # Intenta obtener DATABASE_URL de las variables de entorno
    # Si no está definida, usa una base de datos SQLite local
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
            'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # Desactiva el seguimiento de modificaciones de objetos en SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración para el manejo de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)  # Configura la expiración de la sesión a 10 minutos
    
    # Configuración del correo electrónico
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))  # Si no se proporciona, usar el puerto 587 por defecto (TLS)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'  # Convertir a booleano, por defecto 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'  # Si se necesita SSL, por defecto 'False'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Tu correo electrónico (remitente)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Contraseña del correo electrónico

    # Dirección predeterminada del remitente (siempre a donde se enviarán los correos)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Dirección de correo del administrador
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', MAIL_USERNAME)  # Usa el mismo valor que MAIL_USERNAME si no está definido
    
    # Idiomas soportados
    LANGUAGES = ['en', 'es', 'it', 'ca']  # Inglés, Español, Italiano, Catalán
    
    # Número de cócteles a mostrar por página
    RECIPES_PER_PAGE = 10
    
    # Número de mensajes a mostrar por página
    MESSAGE_PER_PAGE = 2  