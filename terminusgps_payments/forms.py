import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from . import models


class ExpirationDateWidget(widgets.MultiWidget):
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
        widgets = {"customer_profile": widgets.HiddenInput()}
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
        widgets = {
            "card_expiry": ExpirationDateWidget(
                widgets={
                    "month": widgets.DateInput(format=["%m"]),
                    "year": widgets.DateInput(format=["%y"]),
                }
            ),
            "customer_profile": widgets.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        print(f"{args = }")
        print(f"{kwargs = }")
        return super().__init__(*args, **kwargs)

    def clean(self) -> None:
        def clean_fieldset(fieldset):
            if any(fieldset.values()) and not all(fieldset.values()):
                for field, val in fieldset.items():
                    if not val:
                        self.add_error(
                            field,
                            ValidationError(_("This field is required.")),
                        )

        super().clean()
        credit_card_fieldset = {
            "card_number": self.cleaned_data.get("card_number"),
            "card_expiry": self.cleaned_data.get("card_expiry"),
            "card_code": self.cleaned_data.get("card_code"),
        }
        bank_account_fieldset = {
            "account_number": self.cleaned_data.get("account_number"),
            "routing_number": self.cleaned_data.get("routing_number"),
            "account_name": self.cleaned_data.get("account_name"),
            "account_type": self.cleaned_data.get("account_type"),
            "bank_name": self.cleaned_data.get("bank_name"),
        }

        clean_fieldset(credit_card_fieldset)
        clean_fieldset(bank_account_fieldset)
