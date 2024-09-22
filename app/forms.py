from flask_wtf  import FlaskForm
from wtforms import SelectMultipleField, StringField, PasswordField, SubmitField, BooleanField,\
    TextAreaField, widgets
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from app.models import User


from app import cocktailRecommender

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    

class SimpleForm(FlaskForm):
    fruits, alco, nonalco, others = cocktailRecommender.get_general_taxonomy()
    # sort list
    fruits = sorted(fruits)
    alco = sorted(alco)
    nonalco = sorted(nonalco)
    others = sorted(others)
    
    # create a list of value/description tuples
    fruit_list = [(x.title(), x.title()) for x in fruits if x != '']
    alco_list = [(x.title(), x.title()) for x in alco if x != '']
    nonalco_list = [(x.title(), x.title()) for x in nonalco if x != '']
    others_list = [(x.title(), x.title()) for x in others if x != '']
    
    fruits_cb = MultiCheckboxField('Label', choices=fruit_list)
    alco_cb = MultiCheckboxField('Label', choices=alco_list)
    onalco_cb = MultiCheckboxField('Label', choices=nonalco_list)
    fothers_cb = MultiCheckboxField('Label', choices=others_list)
    
    style = {'type': 'button', 'class':'btn btn_primary'}
    submit = SubmitField('Search')
    

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'username'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'email'})
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2')],
                             render_kw={'placeholder': 'password'})
    password2= PasswordField('Repeat Password', validators=[DataRequired()],
                             render_kw={'placeholder': 'password confirmation'})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Choose a differnet username')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please choose a different email')
        
class MessageForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Send')
    
class EvalForm(FlaskForm):
    evaluation = TextAreaField('Evaluation', validators=[DataRequired()])
    submit = SubmitField('Submit')
    

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')