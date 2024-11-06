from datetime import datetime
from flask_mail import Message
from flask import redirect, render_template, session, url_for, flash, current_app, request
from werkzeug.utils import redirect
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from flask_paginate import Pagination

from app import app, db, mail
from app.forms import RegistrationForm, LoginForm, MessageForm, ResetPasswordRequestForm, SimpleForm, ResetPasswordForm
from app.models import CocktailDB, User, UserMessage
from recommender.cocktailRecommender import CocktailRecommender  # Importar el recomendador
from recommender.case_base import Cocktail

# Crear una instancia del recomendador (ajusta los paths si es necesario)
recommender = CocktailRecommender(
    cocktail_file='data/ccc_cocktails.xml',
    taxonomy_file='data/taxonomy_taste.csv',
    general_taxonomy_file='data/general_taxonomy.csv'
)


# Función para enviar correos
def send_email(subject, body, recipient, reply_to=None):
    msg = Message(
        subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.body = body

    if reply_to:
        msg.reply_to = reply_to  # Establecer el campo Reply-To si se proporciona

    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
        

def get_cocktail_pagination(cocktail_list, per_page=10, offset=0):
    """Return a slice of the cocktail list based on pagination parameters."""
    return cocktail_list[offset: offset + per_page]


def get_page_args(page_parameter='page', per_page_parameter='per_page'):
    page = request.args.get(page_parameter, 1, type=int)
    per_page = request.args.get(per_page_parameter, app.config['RECIPES_PER_PAGE'], type=int)
    offset = (page - 1) * per_page
    return page, per_page, offset

@app.route('/')
def index():
    return render_template('index.html', title=_('Home'), languages=current_app.config['LANGUAGES'])

   
@app.route('/register', methods=['GET', 'POST']) 
def register():
    if current_user.is_authenticated:
        return render_template('index.html', title=_('Home'))
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        print(user.username, user.email)
        user.set_password(password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return render_template('index.html', title=_('Home'))
    return render_template('register.html', form=form)


@app.route('/change_language/<language>', methods=['POST'])
def change_language(language):
    # Cambia el idioma solo si el idioma es válido
    if language in app.config['LANGUAGES']:
        session['lang'] = language
        print(session)
    # Redirige de nuevo al lugar donde estaba el usuario
    return redirect(request.referrer)

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already authenticated, redirect to the main page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Load the login form
    form = LoginForm()
    
    # Validate form data once submitted
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is not None:
            if user.check_password(form.password.data):  # Check password
                # Handle "remember me" feature
                session.permanent = form.remember_me.data  # True if user selects "Remember me"
                login_user(user, remember=form.remember_me.data)  # Successful login
                
                flash(_("Welcome, {}!").format(user.username), "success")  # Welcome message
                return redirect(url_for('index'))
            else:
                error = _('Incorrect password')  # Mensaje de error
                return render_template('login.html', form=form, error=error)
        else:
            return redirect(url_for('register'))  # Redirect to registration if user does not exist
    
    # Render the login form if no data has been submitted
    return render_template('login.html', form=form, error='')


@app.route('/specially4u', methods=['GET', 'POST'])
def specially4u():
    form = SimpleForm()
    cocktails = None
    error = ""

    if form.validate_on_submit():
        # Obtener los ingredientes seleccionados
        selected_fruits = form.fruits_cb.data
        selected_alco = form.alco_cb.data
        selected_nonalco = form.onalco_cb.data
        selected_others = form.fothers_cb.data

        # Unir los ingredientes seleccionados en una lista
        selected_ingredients = selected_fruits + selected_alco + selected_nonalco + selected_others

        # Asegurarse de que haya al menos 2 ingredientes seleccionados
        if len(selected_ingredients) < 2:
            error = _("Please select at least two ingredients.")  # Mensaje de error
        else:
            # Obtener recomendaciones de cócteles basados en los ingredientes seleccionados
            recommended_cocktail = recommender.get_recommendation(selected_ingredients)
            cocktails = recommended_cocktail.preparation if recommended_cocktail else []
    
    return render_template('specially4u.html', form=form, cocktails=cocktails, error=error)


@app.route('/message', methods=['GET'])
def message():
    # Obtener los mensajes donde el usuario actual es el remitente o el destinatario
    messages = UserMessage.query.filter(
        (UserMessage.sender_id == current_user.id) | 
        (UserMessage.recipient_id == current_user.id)
    ).order_by(UserMessage.timestamp.desc()).all()
    
    return render_template('message.html', messages=messages, title=_('Your Messages'))


@app.route('/no_recommendation')
def no_recommendation():
    return render_template('no_recommendation.html', title=_('No Recommendations'))


@app.route('/cocktail/<string:cocktail_name>')
def cocktail(cocktail_name):
    # Obtener el número de página actual desde los parámetros de la URL, con un valor predeterminado de 1
    page = request.args.get('page', 1, type=int)
    cocktail = recommender.get_cocktail(cocktail_name)    
    if cocktail:
        # Pasamos el valor de la página actual al template
        return render_template('cocktail.html', cocktail=cocktail, title=cocktail.name, page=page)
    else:
        flash(_('Cocktail not found.'), 'error')  # Mensaje de error si no se encuentra el cóctel
        return redirect(url_for('no_recommendation'))  # Redirigir a la página de no recomendación
    
    
@app.route('/cocktails')
def cocktails():
    # Obtener todos los cócteles de la base de datos a través del recomendador
    cocktail_list = recommender.get_all_cocktails()  # Esta lista debería contener objetos 'Cocktail'

    # Prepara la lista de cócteles para la plantilla de Jinja2
    # Asegúrate de que 'cocktail_list' contenga objetos 'Cocktail'
    cocktail_list = [
        Cocktail(
            name=c.name,
            ingredients=c.ingredients,
            ingredients_quantity_unit=c.ingredients_quantity_unit,
            ingredients_by_taxonomy=c.ingredients_by_taxonomy,
            preparation=c.preparation
        ) for c in cocktail_list
    ]
    
    # Ordena la lista de cócteles por nombre
    cocktail_list = sorted(cocktail_list, key=lambda x: x.name)

    # Paginar la lista de cócteles
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')

    total = len(cocktail_list)
    pagination_cocktails = get_cocktail_pagination(cocktail_list, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap')

    return render_template('cocktails.html',
                           cocktails=pagination_cocktails,
                           page=page,
                           per_page=per_page,
                           pagination=pagination)


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    form = MessageForm()
    if form.validate_on_submit():
        message = UserMessage(
            sender_id=current_user.id,
            recipient_id=1,
            body=form.body.data,
            subject=form.subject.data, 
            timestamp=datetime.utcnow()
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Enviar correo electrónico
        recipient_email = app.config['ADMIN_EMAIL'] 
        send_email(
            subject=form.subject.data, 
            body=_('You have received a new message: {}').format(form.body.data),  # Mensaje de correo
            recipient=recipient_email, 
            reply_to=current_user.email
        )
        
        flash(_('Message sent successfully!'), 'success')  # Mensaje de éxito
        return redirect(url_for('message'))
    
    return render_template('send_message.html', form=form)


@app.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user_email = form.email.data.strip()  # Eliminar espacios en blanco
        print(_('Email submitted: "%(email)s"') % {'email': user_email})  # Imprimir el correo electrónico ingresado
        user = User.query.filter_by(email=user_email).first()
        if user:
            token = user.get_reset_password_token()
            send_email(
                subject=_('Password Reset Request'),
                body=render_template('email_reset_password.txt', user=user, token=token),
                recipient=user_email
            )
            flash(_('An email with instructions to reset your password has been sent.'), 'info')  # Mensaje de información
        else:
            flash(_('If the email is registered, you will receive an email with instructions to reset your password.'), 'info')  # Mensaje de información
        return redirect(url_for('login'))
    return render_template('request_password_reset.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))  # Redirect if the token is invalid
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)  # Update the user's password
        db.session.commit()  # Commit the changes to the database
        flash(_('Your password has been updated.'), 'success')  # Mensaje de éxito
        return redirect(url_for('login'))  # Redirect to the login page
    return render_template('reset_password.html', form=form)

@app.route('/terms_conditions')
def terms_conditions():
    return render_template('terms_conditions.html')


@app.route('/logout')
def logout():
    logout_user()  # Cierra la sesión del usuario
    session.pop('_permanent_session_lifetime', None)  # Opcional: elimina la sesión permanente
    return redirect(url_for('index'))  # Redirige a la página de inicio


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', name=''), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', name=''), 500





