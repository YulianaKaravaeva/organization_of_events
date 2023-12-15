from datetime import datetime

from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.fields import DateField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///org_events.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '#$%^&*'


# Таблица отношения многие-ко-многим для мероприятий и коллективов
class EventTeam(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
  team_id = db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
  number = db.Column(db.Integer)

  event = db.relationship("Event", back_populates="teams")
  team = db.relationship("Team", back_populates="events")


# База данных коллективов
class Team(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  team_name = db.Column(db.String(100), nullable=False)

  users = db.relationship('User', backref='team')
  events = db.relationship("EventTeam", back_populates="team")

  def __repr__(self):
    return '<Team %r>' % self.id


# База данных мероприятий
class Event(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  event_name = db.Column(db.String(100), nullable=False)
  date = db.Column(db.DateTime, nullable=False)
  place = db.Column(db.String(100), nullable=False)
  
  teams = db.relationship("EventTeam", back_populates="event")

  def __repr__(self):
    return '<Event %r>' % self.id


# База данных пользователей (участников)
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_name = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  telephone = db.Column(db.String(120), unique=True)
  
  team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

  def __repr__(self):
    return '<User %r>' % self.id


# База данных админов (ответственных за организацию)
class Admin(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  admin_name = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
    return '<Admin %r>' % self.id


# Класс для настройки даты
class DateForm(FlaskForm):
  date = DateField('DatePicker', format='%Y-%m-%d')


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


if __name__ == '__main__':
  app.run(host="0.0.0.0", debug=True)