from flask import Flask, flash, redirect, render_template, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)

login_manager = LoginManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///org_events.db'
app.config['SECRET_KEY'] = '#$%^&*'
app.config['SECURITY_PASSWORD_SALT'] = "cefcefe"

db = SQLAlchemy(app)

admin = Admin(app)


# Генерация токена для проверки почты
def generate_token(email):
  serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
  return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])


# Подтверждение токена
def confirm_token(token, expiration=3600):
  serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

  try:
      email = serializer.loads(
          token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
      )
      return email

  except Exception:
      return False


# Проверка почты
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
    flash("Ссылка для подтверждения недействительна или срок действия ее истек", "danger")
    
  return redirect("/events")


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
  telephone = db.Column(db.String(120), unique=True)

  # is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
  # confirmed_on = db.Column(db.DateTime, nullable=True)

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


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(UserTeam, db.session))
admin.add_view(ModelView(EventTeam, db.session))
admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(Team, db.session))


# Форма для настройки даты
class DateForm(FlaskForm):
  date = DateField('DatePicker', format='%Y-%m-%d')


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


# Функция загрузчика пользователя
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


# Страница для авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():

    
  if current_user.is_authenticated:
      return redirect('/events')
    
  form = LoginForm()
  
  if request.method == 'POST':
    
    user = User.query.filter_by(email=form.email.data).first()
    user_team = UserTeam.query.filter_by(email=form.email.data).first()
    

    if not user is None and check_password_hash(user.password, form.password.data):

      login_user(user, remember=form.remember_me.data)
      return redirect('/events')

    elif not user_team is None and check_password_hash(user_team.password, form.password.data):

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
      
      return redirect('/login')

    except:
      return 'При добавлении пользователя произошла ошибка'
      
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


# Добавление номера в сценарий мероприятия
@app.route('/events/<int:event_id>/add_team', methods=['GET', 'POST'])
def events_add_team(event_id):

  if request.method == 'POST':

    team_name = request.form['team_name']
    number = int(request.form['number'])

    list_team = EventTeam.query.filter_by(event_id=event_id)

    for el in list_team:
      if el.number >= number:
        el.number += 1

    team = Team.query.filter_by(team_name=team_name).first()
    event_team = EventTeam(event_id=event_id, team_id=team.id, number=number)

    try:
      db.session.add(event_team)
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