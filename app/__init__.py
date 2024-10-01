from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from config import Config
from recommender import CocktailRecommender
from flask import request

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
app.config['RECIPES_PER_PAGE'] = 10
app.config['MESSAGE_PER_PAGE'] = 2

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

babel = Babel(app)

cocktailRecommender = CocktailRecommender(taxonomy_file='data/taxonomy_taste.csv',
                                          cocktail_file='data/ccc_cocktails.xml',
                                          general_taxonomy_file='data/general_taxonomy.csv')


#@babel.localselector
def get_locale():
    #return 'es'
    return request.accept_languages.best_match(app.config['LANGUAGES'])


from app import routes