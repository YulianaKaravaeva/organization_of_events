from itsdangerous import URLSafeTimedSerializer
from src import app


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