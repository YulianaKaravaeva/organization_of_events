# Код моделей

# Таблица отношения многие-ко-многим для мероприятий и коллективов


from flask_login import UserMixin

from app import db, login_manager


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
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_name = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  telephone = db.Column(db.String(120), unique=True)

  team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

  def __repr__(self):
    return '<User %r>' % self.id


# База данных админов (ответственных за организацию)
# class Admin(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   admin_name = db.Column(db.String(80), unique=True, nullable=False)
#   password = db.Column(db.String(80), nullable=False)
#   email = db.Column(db.String(120), unique=True, nullable=False)

#   def __repr__(self):
#     return '<Admin %r>' % self.id
    

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))