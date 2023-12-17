from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from src import app
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.login_registr.forms import (
  LoginForm,
  TeamRegistrationForm,
  UserRegistrationForm,
)
from app.models import Team, User

# Страницы необходимые для регистрации и авторизации


# Страница для регистрации обычного пользователя
@app.route('/registration/user', methods=['POST', 'GET'])
def register_user():

  if current_user.is_authenticated:
      return redirect('/events')

  form = UserRegistrationForm()

  if request.method == 'POST':

    user_name = form.user_name.data
    email = form.email.data
    telephone = form.telephone.data
    password = generate_password_hash(form.password.data)

    user = User(user_name = user_name, email = email, telephone=telephone, password = password)

    try:
      db.session.add(user)
      db.session.commit()

      token = generate_token(email)

      confirm_url = url_for("confirm_email", token=token, _external=True)
      html = render_template("email.html", confirm_url=confirm_url)
      subject = "Пожалуйста, подтвердите вашу электронную почту"
      send_email(user.email, subject, html)

      login_user(user)

      flash("Письмо с подтверждением было отправлено по электронной почте", "success")

      return redirect('/login')

    except Exception as e:
      return 'При добавлении пользователя произошла ошибка' + str(e)

  return render_template('registration_user.html', form=form)


# Страница для регистрации участника
@app.route('/registration/team', methods=['POST', 'GET'])
def register_team():

  if current_user.is_authenticated:
      return redirect('/events')

  form = TeamRegistrationForm()

  if request.method == 'POST':

    user_name = form.user_name.data
    email = form.email.data
    telephone = form.telephone.data
    password = generate_password_hash(form.password.data)

    team = Team.query.filter_by(team_name=form.team.data).first()

    if team is None:
      new_team = Team(team_name=form.team.data)

      try:
        db.session.add(new_team)
        db.session.commit()
        team_id = new_team.id

      except:
        return 'При добавлении пользователя произошла ошибка'

    else:
      team_id = team.id

    user = UserTeam(user_name = user_name, email = email, telephone=telephone, password = password, team_id=team_id)

    try:
      db.session.add(user)
      db.session.commit()
      return redirect('/login')

    except:
      return 'При добавлении пользователя произошла ошибка'

  return render_template('registration_team.html', form=form)


# Страница для авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():


  if current_user.is_authenticated:
      return redirect('/events')

  form = LoginForm()

  if request.method == 'POST':

    user = User.query.filter_by(email=form.email.data).first()
    user_team = UserTeam.query.filter_by(email=form.email.data).first()


    if user is not None and check_password_hash(user.password, form.password.data):

      login_user(user, remember=form.remember_me.data)
      return redirect('/events')

    elif user_team is not None and check_password_hash(user_team.password, form.password.data):

      login_user(user_team, remember=form.remember_me.data)
      return redirect('/events')

    else:
      flash('Неверное имя пользователя или пароль', 'danger')
      return redirect('/login')

  return render_template('login.html', form=form)


# Выход из системы
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')