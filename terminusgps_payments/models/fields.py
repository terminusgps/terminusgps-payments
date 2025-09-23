import pickle

from django.db import models
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement


class AuthorizenetCreditCardField(models.BinaryField):
    description = _("An Authorizenet credit card.")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return pickle.loads(value)

    def to_python(self, value):
        if isinstance(value, ObjectifiedElement):
            return value
        if value is None:
            return None
        return pickle.loads(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return pickle.dumps(value)


class AuthorizenetAddressField(models.BinaryField):
    description = _("An Authorizenet customer address.")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return pickle.loads(value)

    def to_python(self, value):
        if isinstance(value, ObjectifiedElement):
            return value
        if value is None:
            return None
        return pickle.loads(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return pickle.dumps(value)
