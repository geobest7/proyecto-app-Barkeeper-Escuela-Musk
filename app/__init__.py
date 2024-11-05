from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from config import Config
from recommender import CocktailRecommender

# Inicializa la aplicación Flask
app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)

# Inicializa las extensiones
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
babel = Babel(app)

# Inicializa el recomendador de cócteles
cocktailRecommender = CocktailRecommender(
    taxonomy_file='data/taxonomy_taste.csv',
    cocktail_file='data/ccc_cocktails.xml',
    general_taxonomy_file='data/general_taxonomy.csv'
)

# Define la función get_locale antes de la inicialización de Babel
def get_locale():
    # Intenta obtener el idioma de la sesión; si no, usa el mejor idioma disponible según las preferencias del navegador
    return session.get('lang', request.accept_languages.best_match(app.config['LANGUAGES']))

# Inicializa Babel con el selector de idioma
babel.init_app(app, locale_selector=get_locale)

# Inyecta el idioma en el contexto de las plantillas
@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

# Importar las rutas después de la configuración de la aplicación
from app import routes