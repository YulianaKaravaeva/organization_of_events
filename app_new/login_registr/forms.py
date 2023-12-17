from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


# Формы необходимые для регистрации и авторизации


# Форма для авторизации всех пользователей
class LoginForm(FlaskForm):
  email = StringField('Электронная почта', validators=[DataRequired(), Email()])
  password = PasswordField('Пароль', validators=[DataRequired()])
  remember_me = BooleanField('Запомнить меня')
  submit = SubmitField('Войти')


# Форма для регистрации обычного пользователя
class UserRegistrationForm(FlaskForm):
  user_name = StringField('Имя пользователя')
  email = StringField('Электронная почта', validators=[DataRequired(), Email()])
  telephone = StringField('Номер телефон (необязательно)')
  password = PasswordField('Пароль', validators=[DataRequired()])
  repeat_password = PasswordField(
      'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Зарегистрироваться')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()

    if user is not None:
      raise ValidationError('Пользователь с такой почтой уже существует')



# Форма для регистрации участника
class TeamRegistrationForm(FlaskForm):
  user_name = StringField('Имя пользователя')
  email = StringField('Электронная почта', validators=[DataRequired(), Email()])
  telephone = StringField('Номер телефон (необязательно)')
  password = PasswordField('Пароль', validators=[DataRequired()])
  team = StringField('Название коллектива', validators=[DataRequired()])
  repeat_password = PasswordField(
      'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Зарегистрироваться')

  def validate_email(self, email):
      user = User.query.filter_by(email=email.data).first()
      if user is not None:
          raise ValidationError('Пользователь с такой почтой уже существует')
