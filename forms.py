''' Forms to be imported into templates '''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    ''' Login form '''
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    ''' Register form '''
    username = StringField('username', validators=[DataRequired(), Length(
        min=5, max=15,
        message='Username must be between 5 and 15 characters.')])
    profile_pic = FileField('profile_pic')
    fname = StringField('fname', validators=[DataRequired()])
    lname = StringField('lname', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), Length(
        min=5, max=15,
        message='Password must be between 5 and 15 characters.')])


class ChangePassword(FlaskForm):
    ''' Change password form '''
    username = StringField('username', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo(
        'confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('confirm_password')


class ContactForm(FlaskForm):
    ''' Contact form '''
    full_name = StringField('Full name', validators=[DataRequired()])
    username = StringField('username', validators=[Optional()])
    email = EmailField('email', validators=[DataRequired()])
    message = TextAreaField('message', render_kw={"rows": 5, "cols": 30})
