from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, PasswordField, SubmitField, BooleanField, TextAreaField, widgets
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from app.models import User
from flask_babel import _
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
    
    fruits_cb = MultiCheckboxField(_('Fruits'), choices=fruit_list)
    alco_cb = MultiCheckboxField(_('Alcoholic Beverages'), choices=alco_list)
    onalco_cb = MultiCheckboxField(_('Non-Alcoholic Beverages'), choices=nonalco_list)
    fothers_cb = MultiCheckboxField(_('Others'), choices=others_list)
    
    style = {'type': 'button', 'class':'btn btn_primary'}
    submit = SubmitField(_('Search'))
    

class LoginForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired()], render_kw={'placeholder': _('username')})
    password = PasswordField(_('Password'), validators=[DataRequired()], render_kw={'placeholder': _('password')})
    remember_me = BooleanField(_('Remember Me'))
    submit = SubmitField(_('Login'))


class RegistrationForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired()], render_kw={'placeholder': _('username')})
    email = StringField(_('Email'), validators=[DataRequired(), Email()], render_kw={'placeholder': _('email')})
    password = PasswordField(_('Password'), validators=[DataRequired(), EqualTo('password2')],
                             render_kw={'placeholder': _('password')})
    password2 = PasswordField(_('Repeat Password'), validators=[DataRequired()],
                             render_kw={'placeholder': _('password confirmation')})
    submit = SubmitField(_('Register'))
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Choose a different username'))
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please choose a different email'))

       
class MessageForm(FlaskForm):
    subject = StringField(_('Subject'), validators=[DataRequired()])
    body = TextAreaField(_('Body'), validators=[DataRequired()])
    submit = SubmitField(_('Send'))
 
    
class EvalForm(FlaskForm):
    evaluation = TextAreaField(_('Evaluation'), validators=[DataRequired()])
    submit = SubmitField(_('Submit'))
    

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_('Request Password Reset'))
 
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField(_('New Password'), validators=[DataRequired()], render_kw={'placeholder': _('New Password')})
    password2 = PasswordField(_('Repeat Password'), validators=[DataRequired(), EqualTo('password')],
                              render_kw={'placeholder': _('Confirm New Password')})
    submit = SubmitField(_('Reset Password'))