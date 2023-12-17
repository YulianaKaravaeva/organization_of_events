# # Этот файл сообщает Python, что папка app — пакет Python
# import os

# from flask import Flask
# from flask_admin import Admin
# from flask_login import LoginManager
# from flask_mail import Mail
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# # Настройка приложения
# app.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopementConfig')


# # Инициализация расширений
# login_manager = LoginManager(app)
# db = SQLAlchemy(app)
# admin = Admin(app)
# mail = Mail(app)

# db.create_all()