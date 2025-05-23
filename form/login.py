from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
