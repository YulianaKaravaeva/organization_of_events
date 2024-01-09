# Этот файл сообщает Python, что папка app — пакет Python
from flask import Flask


from .extension import db, login_manager, admin, mail


# Фабрика приложения
def create_app():
  app = Flask(__name__)
  app.config.from_object("config.DevelopmentConfig")

  
  
  # with app.test_request_context():
  #     db.create_all()
  admin.init_app(app)
  mail.init_app(app)
  login_manager.init_app(app)
  db.init_app(app)
  with app.app_context():
      db.create_all()

  import app.event.view as events
  import app.login_registr.view as login_registr
  import app.team.view as teams

  app.register_blueprint(events.module)
  app.register_blueprint(login_registr.module)
  app.register_blueprint(teams.module)
  
  return app
