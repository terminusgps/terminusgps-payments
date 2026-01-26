import datetime

from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class ExpirationDateWidget(forms.widgets.MultiWidget):
    def __init__(self, **kwargs) -> None:
        return super().__init__(**kwargs)

    def decompress(self, value):
        if value:
            return [value.month, value.year]
        return [None, None]


class ExpirationDateField(forms.MultiValueField):
    def __init__(self, fields=(), widget=None, **kwargs) -> None:
        return super().__init__(
            error_messages={},
            fields=(
                forms.DateField(input_formats=["%m", "%-m"]),
                forms.DateField(input_formats=["%y"]),
            ),
            widget=widget,
            require_all_fields=False,
            **kwargs,
        )

    def compress(self, data_list):
        if data_list:
            return datetime.date(
                day=1, month=data_list[0].month, year=data_list[1].year
            )
        return None


class CustomerAddressProfileCreateForm(forms.ModelForm):
    class Meta:
        model = models.CustomerAddressProfile
        fields = [
            "first_name",
            "last_name",
            "company",
            "address",
            "city",
            "state",
            "country",
            "zip",
            "phone_number",
            "customer_profile",
        ]
        widgets = {"customer_profile": forms.widgets.HiddenInput()}
        help_texts = {
            "first_name": _("Enter a first name."),
            "last_name": _("Enter a last name."),
            "company": _("Optional. Enter a company name."),
            "address": _("Enter a house number + street."),
            "city": _("Enter a city."),
            "state": _("Enter a state."),
            "zip": _("Enter a ZIP code."),
            "country": _("Enter a country."),
            "phone_number": _(
                "Optional. Enter an E.164-formatted phone number. Ex: 17139045262"
            ),
        }


class CustomerPaymentProfileCreateForm(forms.ModelForm):
    class Meta:
        model = models.CustomerPaymentProfile
        field_classes = {"card_expiry": ExpirationDateField}
        fields = [
            "first_name",
            "last_name",
            "company",
            "address",
            "city",
            "state",
            "country",
            "zip",
            "phone_number",
            "card_number",
            "card_expiry",
            "card_code",
            "account_number",
            "routing_number",
            "account_name",
            "account_type",
            "bank_name",
            "customer_profile",
        ]
        help_texts = {
            "first_name": _("Enter a first name."),
            "last_name": _("Enter a last name."),
            "company": _("Optional. Enter a company name."),
            "address": _("Enter a house number + street."),
            "city": _("Enter a city."),
            "state": _("Enter a state."),
            "zip": _("Enter a ZIP code."),
            "country": _("Enter a country."),
            "phone_number": _(
                "Optional. Enter an E.164-formatted phone number. Ex: 17139045262"
            ),
            "card_number": _("Enter a card number."),
            "card_expiry": _("Enter an expiration date month and year."),
            "card_code": _("Enter a 3-4 digit CCV code."),
            "account_number": _("Enter an account number."),
            "routing_number": _("Enter a routing number."),
            "account_name": _("Enter an account holder name."),
            "bank_name": _("Enter a bank name."),
            "account_type": _("Select a bank account type."),
        }
        widgets = {"customer_profile": forms.widgets.HiddenInput()}
