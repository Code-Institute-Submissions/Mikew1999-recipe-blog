''' Forms to be imported into templates '''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    ''' Login form '''
    username = StringField('username', validators=[DataRequired(), Length(
        min=5, max=15,
        message='Username must be between 5 and 15 characters.')])
    password = PasswordField('password', validators=[DataRequired(), Length(
        min=5, max=15,
        message='Password must be between 5 and 15 characters.')])


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
