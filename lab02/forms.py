import datetime
from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, FloatField
from wtforms.widgets import HiddenInput
from wtforms.validators import DataRequired, NumberRange

from db import db


def date2str(date: Optional[datetime.datetime]):
    if date:
        return date.strftime("%Y-%m-%d")


class CreateSerialForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    country = StringField('Страна')
    genre = StringField('Жанр')
    age_limits = IntegerField("Возрастное ограничение", validators=[NumberRange(0, 99)])
    start_date = DateField("Дата выхода", filters=[date2str])
    release_date = DateField("Дата завершения", filters=[date2str])
    rating = FloatField("Рейтинг", validators=[NumberRange(0, 10)])

    def save(self):
        data = {
            name: f.data
            for name, f in self._fields.items()
            if f is not None and not isinstance(f.widget, HiddenInput)
        }
        data['created_at'] = datetime.datetime.now().isoformat()

        return db.serials.insert_one(data)
