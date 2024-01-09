from flask import redirect, render_template, request, Blueprint

from app import db
from app.models import Event, EventTeam, Team, User

# Страницы с командами

module = Blueprint('teams', __name__)

# Страница мероприятия (порядок номеров мероприятия)
@module.route('/events/<int:id>')
def event_detail(id):
  event = Event.query.get_or_404(id)
  list_event = EventTeam.query.filter_by(event_id=id).all()
  #db.sessions.query(EventTeam).filter(EventTeam.event_id==id).all()
  return render_template("event_detail.html", event=event, list_event=list_event)


# Удаление номера из сценария мероприятия
@module.route('/events/<int:event_id>/<int:team_id>/delete_team')
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
@module.route('/events/<int:event_id>/add_team', methods=['GET', 'POST'])
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
@module.route('/teams')
def teams():
  teams = Team.query.order_by(Team.team_name).all()
  return render_template("teams.html", teams=teams)


# Страница добавления нового коллектива
@module.route('/teams/add', methods=['GET', 'POST'])
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
@module.route('/teams/<int:id>')
def team_detail(id):
  team = Team.query.get_or_404(id)
  list_user = User.query.filter_by(team_id=id).all()
  return render_template("team_detail.html", team=team, list_user=list_user)
