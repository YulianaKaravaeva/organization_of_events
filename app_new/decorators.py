from functools import wraps

from flask import flash, redirect
from flask_login import current_user


#Декоратор маршрутов (доступ только подтвержденным пользователям)
def check_is_confirmed(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    #@wraps(func)
    if current_user.is_confirmed is False:

      flash("Пожалуйста подтвердите Вашу электроннную почту!", "warning")
      return redirect('/inactive')

    return func(*args, **kwargs)

  return decorated_function