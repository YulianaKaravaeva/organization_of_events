# Код классов форм

from flask_wtf import FlaskForm
from wtforms import (
  BooleanField,
  StringField,
  SubmitField,
)
from wtforms.fields import DateField
from wtforms.validators import DataRequired


# Форма для настройки даты
class DateForm(FlaskForm):
  date = DateField('DatePicker', format='%Y-%m-%d')