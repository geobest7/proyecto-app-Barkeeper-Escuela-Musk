from datetime import datetime
from flask_mail import Message
from flask import redirect, render_template, session, url_for, flash, current_app, request
from werkzeug.utils import redirect
from flask_login import current_user, login_user, logout_user
from flask_babel import _

from app import app, db, mail
from app.forms import RegistrationForm, LoginForm, MessageForm, EvalForm, ResetPasswordRequestForm, SimpleForm
from app.models import User, UserMessage
from recommender.cocktailRecommender import CocktailRecommender  # Importar el recomendador

# Función para enviar correos
def send_email(subject, body):
    msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[current_user.email])
    msg.body = body
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

# Crear una instancia del recomendador (ajusta los paths si es necesario)
recommender = CocktailRecommender(
    cocktail_file='data/ccc_cocktails.xml',
    taxonomy_file='data/taxonomy_taste.csv',
    general_taxonomy_file='data/general_taxonomy.csv'
)


@app.route('/')
def index():
        return render_template('index.html', title='Home')
    
@app.route('/registrer', methods=['GET', 'POST']) 
def registrer():
    if current_user.is_authenticated:
        return render_template('index.html', title='Home')
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        print(user.username, user.email)
        user.set_password(password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return render_template('index.html', title='Home')
    return render_template('registrer.html', form=form)

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
                
                flash(f"Welcome, {user.username}!", "success")  # Welcome message
                return redirect(url_for('index'))
            else:
                error = 'Incorrect password'
                return render_template('login.html', form=form, error=error)
        else:
            return redirect(url_for('registrer'))  # Redirect to registration if user does not exist
    
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
            error = "Por favor, selecciona al menos dos ingredientes."
        else:
            # Obtener recomendaciones de cócteles basados en los ingredientes seleccionados
            recommended_cocktail = recommender.get_recommendation(selected_ingredients)
            cocktails = recommended_cocktail.preparation if recommended_cocktail else []
    
    return render_template('specially4u.html', form=form, cocktails=cocktails, error=error)

@app.route('/message', methods=['GET'])
def message():
    messages = current_user.message_recived.order_by(UserMessage.timestamp.desc()).all()
    return render_template('message.html', messages=messages, title='Your Messages')


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
        send_email(subject=form.subject.data, body=form.body.data)
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('message'))
    
    return render_template('send_message.html', form=form)

@app.route('/logout')
def logout():
    logout_user()  # Cierra la sesión del usuario
    session.pop('_permanent_session_lifetime', None)  # Opcional: elimina la sesión permanente
    return redirect(url_for('index'))  # Redirige a la página de inicio