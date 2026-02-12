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

    def clean(self):
        cleaned_data = super().clean()
        shipping_address_fields = [
            cleaned_data.get("first_name"),
            cleaned_data.get("last_name"),
            cleaned_data.get("address"),
            cleaned_data.get("city"),
            cleaned_data.get("state"),
            cleaned_data.get("country"),
            cleaned_data.get("zip"),
        ]
        if not all(shipping_address_fields):
            raise ValidationError(
                _("Please fill out all required shipping address fields."),
                code="invalid",
            )


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
            "expiry_date": ExpirationDateWidget(
                widgets={
                    "month": widgets.DateInput(format=["%m"]),
                    "year": widgets.DateInput(format=["%y"]),
                }
            ),
            "customer_profile": widgets.HiddenInput(),
        }

    def clean(self) -> None:
        cleaned_data = super().clean()
        billing_address_fields = [
            cleaned_data.get("first_name"),
            cleaned_data.get("last_name"),
            cleaned_data.get("address"),
            cleaned_data.get("city"),
            cleaned_data.get("state"),
            cleaned_data.get("country"),
            cleaned_data.get("zip"),
        ]
        credit_card_fields = [
            cleaned_data.get("card_number"),
            cleaned_data.get("card_expiry"),
            cleaned_data.get("card_code"),
        ]
        bank_account_fields = [
            cleaned_data.get("account_number"),
            cleaned_data.get("routing_number"),
            cleaned_data.get("account_name"),
            cleaned_data.get("account_type"),
            cleaned_data.get("bank_name"),
        ]

        if not any(billing_address_fields):
            raise ValidationError(
                _("Please fill out all required billing address fields."),
                code="invalid",
            )
        if any(credit_card_fields) and any(bank_account_fields):
            raise ValidationError(
                _(
                    "Please fill out all credit card fields or bank account fields, not both."
                ),
                code="invalid",
            )
        if any(credit_card_fields) and not all(credit_card_fields):
            raise ValidationError(
                _("Please fill out all credit card fields."), code="invalid"
            )
        if any(bank_account_fields) and not all(bank_account_fields):
            raise ValidationError(
                _("Please fill out all bank account fields."), code="invalid"
            )


class SubscriptionCreateForm(forms.ModelForm):
    class Meta:
        model = models.Subscription
        fields = [
            "name",
            "amount",
            "address_profile",
            "payment_profile",
            "total_occurrences",
            "trial_occurrences",
            "trial_amount",
            "interval_length",
            "interval_unit",
        ]
        widgets = {
            "address_profile": forms.widgets.Select(
                attrs={"aria-required": "true"}
            ),
            "payment_profile": forms.widgets.Select(
                attrs={"aria-required": "true"}
            ),
            "name": forms.widgets.TextInput(attrs={"aria-required": "true"}),
            "amount": forms.widgets.TextInput(attrs={"aria-required": "true"}),
            "total_occurrences": forms.widgets.HiddenInput(),
            "trial_occurrences": forms.widgets.HiddenInput(),
            "trial_amount": forms.widgets.HiddenInput(),
            "interval_length": forms.widgets.HiddenInput(),
            "interval_unit": forms.widgets.HiddenInput(),
        }

    def __init__(self, *args, **kwargs) -> None:
        customer_profile = kwargs.pop("customer_profile", None)
        address_qs = (
            customer_profile.address_profiles.all()
            if customer_profile is not None
            else models.CustomerAddressProfile.objects.none()
        )
        payment_qs = (
            customer_profile.payment_profiles.all()
            if customer_profile is not None
            else models.CustomerPaymentProfile.objects.none()
        )

        address_field = self.base_fields["address_profile"]
        payment_field = self.base_fields["payment_profile"]
        address_field.queryset = address_qs
        address_field.empty_label = None
        payment_field.queryset = payment_qs
        payment_field.empty_label = None
        return super().__init__(*args, **kwargs)


class SubscriptionUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Subscription
        fields = ["address_profile", "payment_profile"]
        widgets = {
            "address_profile": forms.widgets.Select(
                attrs={"aria-required": "true"}
            ),
            "payment_profile": forms.widgets.Select(
                attrs={"aria-required": "true"}
            ),
        }
