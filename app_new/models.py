from flask_login import UserMixin
from scr import app

from app import db

# Код моделей базы данных


#Таблица отношения многие-ко-многим для мероприятий и коллективов
class EventTeam(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
  team_id = db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
  number = db.Column(db.Integer)

  event = db.relationship("Event", back_populates="teams")
  team = db.relationship("Team", back_populates="events")

  def __repr__(self):
    return '<Team %r>' % id


# База данных коллективов
class Team(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  team_name = db.Column(db.String(100), nullable=False)

  users = db.relationship('UserTeam', backref='team')
  events = db.relationship("EventTeam", back_populates="team")

  def __repr__(self):
    return '<Team %r>' % self.team_name


# База данных мероприятий
class Event(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  event_name = db.Column(db.String(100), nullable=False)
  date = db.Column(db.DateTime, nullable=False)
  place = db.Column(db.String(100), nullable=False)

  teams = db.relationship("EventTeam", back_populates="event")

  def __repr__(self):
    return '<Event %r>' % self.event_name


# База данных обычных пользователей
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_name = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  telephone = db.Column(db.String(120))

  is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
  confirmed_on = db.Column(db.DateTime, nullable=True)

  def __repr__(self):
    return '<User %r>' % self.user_name


# База данных обычных участников
class UserTeam(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_name = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  telephone = db.Column(db.String(120), unique=True)

  is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
  confirmed_on = db.Column(db.DateTime, nullable=True)

  team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

  def __repr__(self):
    return '<UserTeam %r>' % self.user_name