import datetime
from typing import Optional
from bson import ObjectId
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, IntegerField, FormField, FieldList, Form, DateField, ValidationError
from wtforms.widgets import HiddenInput
from wtforms.validators import DataRequired, NumberRange

from db import db
from widgets import CooperativeMembershipListWidget, OwnerForeignKeyWidget


def date2str(date: Optional[datetime.datetime]):
    if date:
        return date.strftime("%Y-%m-%d")


class CreateOwnerForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    residence = StringField('Район проживания')
    address = StringField('Адрес')
    passport = StringField('Паспортные данные')

    def save(self):
        data = {
            name: f.data
            for name, f in self._fields.items()
            if f is not None and not isinstance(f.widget, HiddenInput)
        }

        return db.owners.insert_one(data)


class RegisterCooperativeForm(FlaskForm):
    class MembershipForm(Form):
        number = IntegerField('Номер регистрации', validators=[DataRequired(), NumberRange(min=1)])
        owner_id = StringField('Владелец', validators=[DataRequired()], widget=OwnerForeignKeyWidget())
        amount = IntegerField('Размер пая', validators=[DataRequired(), NumberRange(min=1)])
        date = DateField('Дата', validators=[DataRequired()], default=datetime.datetime.today)

    name = StringField('Название', validators=[DataRequired()])
    profile = StringField('Район размещения', default="Россия")
    workers_number = IntegerField('Количество работников (человек)', validators=[NumberRange(min=1)], default=10)
    residence = StringField('Профиль', default="Разное")
    memberships = FieldList(FormField(MembershipForm), 'Членство', min_entries=1, widget=CooperativeMembershipListWidget())

    def save(self):
        cooperative_id = db.cooperatives.insert_one({
            'name': self.name.data,
            'profile': self.profile.data,
            'workers_number': self.workers_number.data,
            'residence': self.residence.data,
            'capital_amount': sum(member['amount'] for member in self.memberships.data),
        }).inserted_id

        db.memberships.insert_many([
            {
                'number': member['number'],
                'owner_id': ObjectId(member['owner_id']),
                'amount': member['amount'],
                'date': date2str(member['date']),
                'cooperative_id': cooperative_id,
            }
            for member in self.memberships.data
        ])


class TransferMembershipForm(FlaskForm):
    buyer_id = StringField('Получатель пая', validators=[DataRequired()], widget=OwnerForeignKeyWidget())
    cooperative_approve = BooleanField('Согласие кооператива было получено?')
    amount = IntegerField('Размер пая', validators=[DataRequired(), NumberRange(min=1)])
    number = IntegerField('Номер регистрации', validators=[DataRequired(), NumberRange(min=1)])
    date = DateField('Дата', validators=[DataRequired()], default=datetime.datetime.today)

    def __init__(self, membership, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.membership = membership
        self.cooperative_id = self.membership.get("cooperative_id")
        self.buyer_membership = None

    def validate_number(self, field):
        number = field.data
        last_membership = db.memberships.find_one(
            {
                "cooperative_id": self.cooperative_id,
            },
            sort=[('number', -1)],
        )

        if last_membership and last_membership.get("number") >= number:
            raise ValidationError(f"Номер должен быть больше {last_membership.get('number')}")

    def validate_buyer_id(self, field):
        buyer_id = ObjectId(field.data)
        if buyer_id == self.membership.get("owner_id"):
            raise ValidationError(f"Владелец и получатель должны отличаться")

        self.buyer_membership = db.memberships.find_one(
            {
                "owner_id": buyer_id,
                "cooperative_id": self.cooperative_id,
            },
            sort=[('number', -1)],
        )
        if self.buyer_membership and self.buyer_membership.get("amount", 0) <= 0:
            self.buyer_membership = None

    def validate_amount(self, field):
        owner_amount = self.membership["amount"]
        if field.data > owner_amount:
            raise ValidationError(f"Владелец не может передать пай, больше чем {owner_amount}")

    def validate(self, extra_validators=None) -> bool:
        valid = super().validate(extra_validators)

        if not self.buyer_membership and not self.cooperative_approve.data:
            self.cooperative_approve.errors.append(
                "Передача пая гражданину, не являющемуся членом кооператива "
                "допускается лишь с согласия кооператива"
            )
            valid = False

        return valid

    def save(self):
        buyer_amount = self.amount.data
        if self.buyer_membership:
            buyer_amount += self.buyer_membership.get('amount', 0)

        db.memberships.insert_many([{
            'number': self.number.data,
            'owner_id': ObjectId(self.buyer_id.data),
            'amount': buyer_amount,
            'date': date2str(self.date.data),
            'cooperative_id': self.cooperative_id,
        }, {
            'number': self.number.data,
            'owner_id': self.membership['owner_id'],
            'amount': self.membership['amount'] - self.amount.data,
            'date': date2str(self.date.data),
            'cooperative_id': self.cooperative_id,
        }])
