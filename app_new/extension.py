from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin()
mail = Mail()