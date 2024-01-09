# Код классов форм для страниц с мероприятиями

from flask_wtf import FlaskForm
from wtforms.fields import DateField


# Форма для настройки даты
class DateForm(FlaskForm):
  date = DateField('DatePicker', format='%Y-%m-%d')