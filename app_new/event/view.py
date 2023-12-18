from flask import Blueprint, redirect, render_template, request

from app.models import Event

from .forms import DateForm

from app.decorators import check_is_confirmed

from app.extension import db

module = Blueprint('events', __name__)

# Страницы с мероприятиями

# Главная страница (страница с мероприятиями)
#@check_is_confirmed
@module.route('/events')
@check_is_confirmed
def events():
  events = Event.query.order_by(Event.date).all()
  return render_template("events.html", events=events)

# Страница добавления нового мероприятия
@module.route('/events/add', methods=['GET', 'POST'])
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
@module.route('/events/<int:id>/delete')
def events_delete(id):
  event = Event.query.get_or_404(id)

  try:
    db.session.delete(event)
    db.session.commit()
    return redirect('/events')

  except:
    return 'При удалении мероприятия произошла ошибка'


# Страница редактирования мероприятия
@module.route('/events/<int:id>/update', methods=['GET', 'POST'])
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

