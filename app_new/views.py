# Маршруты и функции представления

from flask import flash, redirect, render_template, request
from flask_login import current_user, login_user
from werkzeug.security import generate_password_hash

from app import app

from .forms import DateForm, LoginForm
from .models import User, db


# Страница для авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():

  if current_user.is_authenticated:
      return redirect('/events')

  form = LoginForm()

  if form.validate_on_submit():
      user = User.query.filter_by(user_name=form.user_name.data).first()
      if user is None or not user.check_password(form.password.data):
          flash('Invalid username or password')
          return redirect('/login')
      login_user(user, remember=form.remember_me.data)
      return redirect('/events')
  return render_template('login.html', title='Sign In', form=form)


# Страница для регистрации
@app.route('/registration', methods=['POST', 'GET'])
def register():

  if request.method == 'POST':

    user_name = request.form['user_name']
    password = request.form['password']
    request.form['repeat_password']
    email = request.form['email']
    telephone = request.form['telephone']

    has_password = generate_password_hash(password)

    user = User(user_name=user_name, password=has_password, email=email, telephone=telephone)

    try:
      db.session.add(user)
      db.session.commit()
      return redirect('/login')

    except:
      return 'При добавлении пользователя произошла ошибка'


  else:
    return render_template('registration.html')


# Главная страница (страница с мероприятиями)
@app.route('/')
@app.route('/events')
def events():
  events = Event.query.order_by(Event.date).all()
  return render_template("events.html", events=events)

# Страница добавления нового мероприятия
@app.route('/events/add', methods=['GET', 'POST'])
def events_add():
  form = DateForm()

  if request.method == 'POST':

    event_name = request.form['event_name']
    place = request.form['place']
    date = form.date.data

    event = Event(event_name=event_name, place=place, date=date)

    try:
      db.session.add(event)
      db.session.commit()
      return redirect('/events')

    except:
      return 'При добавлении мероприятия произошла ошибка'

  else:
    return render_template("events_add.html", form=form)


# Удаление мероприятия
@app.route('/events/<int:id>/delete')
def events_delete(id):
  event = Event.query.get_or_404(id)

  try:
    db.session.delete(event)
    db.session.commit()
    return redirect('/events')

  except:
    return 'При удалении мероприятия произошла ошибка'


# Страница редактирования мероприятия
@app.route('/events/<int:id>/update', methods=['GET', 'POST'])
def events_update(id):
  event = Event.query.get_or_404(id)
  form = DateForm()

  if request.method == 'POST':

    event.event_name = request.form['event_name']
    event.place = request.form['place']
    event.date = form.date.data

    try:
      db.session.commit()
      return redirect('/events')

    except:
      return 'При редактировании мероприятия произошла ошибка'

  else:
    return render_template("event_update.html", event=event, form=form)


# Страница мероприятия (порядок номеров мероприятия)
@app.route('/events/<int:id>')
def event_detail(id):
  event = Event.query.get_or_404(id)
  list_event = EventTeam.query.filter_by(event_id=id).all()
  #db.sessions.query(EventTeam).filter(EventTeam.event_id==id).all()
  return render_template("event_detail.html", event=event, list_event=list_event)


# Удаление номера из сценария мероприятия
@app.route('/events/<int:event_id>/<int:team_id>/delete_team')
def events_delete_team(event_id, team_id):
  team = Team.query.get_or_404(team_id)

  try:

    list_team = EventTeam.query.filter_by(event_id=event_id)
    number_team = list_team.filter_by(team_id=team_id)[0].number
    for el in list_team:
      if el.number > number_team:
        el.number -= 1

    db.session.delete(team)
    db.session.delete(EventTeam.query.filter_by(event_id=event_id, team_id=team_id))
    db.session.commit()

    return redirect('/events/' + str(event_id))

  except:
    return 'При удалении мероприятия произошла ошибка'


# Добавление номера из сценария мероприятия
@app.route('/events/<int:event_id>/add_team', methods=['GET', 'POST'])
def events_add_team(event_id):

  if request.method == 'POST':

    team_name = request.form['team_name']
    number = request.form['number']

    list_team = EventTeam.query.filter_by(event_id=event_id)

    for el in list_team:
      if el.number >= number:
        el.number += 1

    team = Team(team_name=team_name)
    event_team = EventTeam(event_id=event_id, team_id=team.id, number=number)

    try:
      db.session.add_all([team, event_team])
      db.session.commit()
      return redirect('/events/' + str(event_id))

    except:
      return 'При добавлении мероприятия произошла ошибка'

  else:
    return render_template("events_add_team.html", event_id=event_id)


# Страница с коллективами
@app.route('/teams')
def teams():
  teams = Team.query.order_by(Team.team_name).all()
  return render_template("teams.html", teams=teams)


# Страница добавления нового коллектива
@app.route('/teams/add', methods=['GET', 'POST'])
def teams_add():

  if request.method == 'POST':

    team_name = request.form['team_name']

    team = Team(team_name=team_name)

    try:
      db.session.add(team)
      db.session.commit()
      return redirect('/teams')

    except:
      return 'При добавлении коллектива произошла ошибка'

  else:
    return render_template("teams_add.html")


# Страница коллектива
@app.route('/teams/<int:id>')
def team_detail(id):
  team = Team.query.get_or_404(id)
  list_user = User.query.filter_by(team_id=id).all()
  return render_template("team_detail.html", team=team, list_user=list_user)


# Проверка почты
@app.route("/confirm/<token>")
@login_required
def confirm_email(token):

  if current_user.is_confirmed:
    flash("Account already confirmed.", "success")
    return redirect("/events")

  email = confirm_token(token)
  user = User.query.filter_by(email=current_user.email).first_or_404()

  if user.email == email:

    user.is_confirmed = True
    user.confirmed_on = datetime.now()
    db.session.add(user)
    db.session.commit()
    flash("Подтверждение прошло успешно!", "success")

  else:
    flash("Ссылка недействительна или срок действия ее истек", "danger")

  return redirect("/events")