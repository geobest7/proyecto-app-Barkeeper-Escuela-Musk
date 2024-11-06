from flask import Flask, g, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel, force_locale
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



def get_locale():
    return session.get('lang', request.accept_languages.best_match(app.config['LANGUAGES']))


app.jinja_env.globals['get_locale'] = get_locale

babel = Babel(app, locale_selector=get_locale)


# Inicializa el recomendador de cócteles
cocktailRecommender = CocktailRecommender(
    taxonomy_file='data/taxonomy_taste.csv',
    cocktail_file='data/ccc_cocktails.xml',
    general_taxonomy_file='data/general_taxonomy.csv'
)


# Importar las rutas después de la configuración de la aplicación
from app import routes
