''' Forms to be imported into templates '''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    ''' Login form '''
    username = StringField('username', validators=[DataRequired(), Length(
        min=5, max=15,
        message='Username must be between 5 and 15 characters.')])
    password = PasswordField('password', validators=[DataRequired(), Length(
        min=5, max=15,
        message='Password must be between 5 and 15 characters.')])
