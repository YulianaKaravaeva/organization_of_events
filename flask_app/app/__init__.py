# Этот файл сообщает Python, что папка app — пакет Python
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Создает объект приложения как экземпляр класса Flask
app = Flask(__name__)

# Настройка приложения
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopementConfig')

# Инициализация расширений
login_manager = LoginManager(app)
db = SQLAlchemy(app)


