import typing
from datetime import date

from authorizenet import apicontractsv1
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from terminusgps_payments.models import Subscription, SubscriptionPlan


def luhn_check(card_number: str) -> bool:
    if not card_number.isdigit():
        return False
    if len(card_number) > 16:
        return False
    if len(card_number) < 13:
        return False
    checksum = 0
    odds = card_number[::-1][::2]
    evens = card_number[::-1][1::2]
    for digit in odds:
        checksum += int(digit)
    for digit in evens:
        number = int(digit) * 2
        if number >= 10:
            number = (number // 10) + (number % 10)
        checksum += number
    return checksum % 10 == 0


class AuthorizenetContractForm(forms.Form):
    contract_cls = None

    def build_contract(self):
        if self.contract_cls is None:
            raise ValueError("'contract_cls' wasn't set.")
        if not self.is_valid():
            raise ValueError("Form was invalid.")
        contract = self.contract_cls()
        for field, value in self.cleaned_data.items():
            if value:
                setattr(contract, field, value)
        return contract


class AddressForm(AuthorizenetContractForm):
    contract_cls = apicontractsv1.customerAddressType

    firstName = forms.CharField(max_length=50)
    lastName = forms.CharField(max_length=50)
    company = forms.CharField(max_length=50, required=False)
    address = forms.CharField(max_length=60)
    city = forms.CharField(max_length=40)
    state = forms.CharField(max_length=40)
    zip = forms.CharField(max_length=20)
    country = forms.CharField(max_length=60, required=False)
    phoneNumber = forms.CharField(max_length=25, required=False)
    faxNumber = forms.CharField(max_length=25, required=False)


class CreditCardForm(AuthorizenetContractForm):
    contract_cls = apicontractsv1.creditCardType

    cardNumber = forms.CharField(max_length=16, min_length=13)
    cardCode = forms.CharField(max_length=4, min_length=3)
    expirationDate = forms.DateField(input_formats=["%Y-%m"])

    @typing.override
    def build_contract(self):
        if self.contract_cls is None:
            raise ValueError("'contract_cls' wasn't set.")
        if not self.is_valid():
            raise ValueError("Form was invalid.")
        cardNumber = self.cleaned_data["cardNumber"]
        cardCode = self.cleaned_data["cardCode"]
        expirationDate = self.cleaned_data["expirationDate"]
        contract = self.contract_cls()
        contract.cardNumber = cardNumber
        contract.cardCode = cardCode
        contract.expirationDate = expirationDate.strftime("%Y-%m")
        return contract

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data:
            if cardNumber := cleaned_data.get("cardNumber"):
                if not luhn_check(cardNumber):
                    self.add_error(
                        "cardNumber",
                        ValidationError(
                            _("Invalid card number."), code="invalid"
                        ),
                    )
            if expirationDate := cleaned_data.get("expirationDate"):
                if date.today() > expirationDate:
                    self.add_error(
                        "expirationDate",
                        ValidationError(
                            _("Expiration date cannot be in the past."),
                            code="invalid",
                        ),
                    )


class BankAccountForm(AuthorizenetContractForm):
    contract_cls = apicontractsv1.bankAccountType

    accountType = forms.ChoiceField(
        choices=[
            ("checking", _("Checking")),
            ("savings", _("Savings")),
            ("businessChecking", _("Business Checking")),
        ]
    )
    accountNumber = forms.CharField(max_length=17)
    routingNumber = forms.CharField(max_length=9)
    nameOnAccount = forms.CharField(max_length=22)
    bankName = forms.CharField(max_length=50)

    @typing.override
    def build_contract(self):
        contract = super().build_contract()
        contract.echeckType = "PPD"
        return contract


class CreateSubscriptionForm(forms.ModelForm):
    payment_profile = forms.ChoiceField(choices=[])
    shipping_profile = forms.ChoiceField(choices=[])
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.all(),
        widget=forms.widgets.Select(
            attrs={
                "hx-get": reverse_lazy(
                    "terminusgps_payments:subscription plan details"
                ),
                "hx-trigger": "load, change",
                "hx-target": "#subscription-plan",
            }
        ),
    )

    class Meta:
        model = Subscription
        fields = ["plan"]


class UpdateSubscriptionForm(forms.Form):
    payment_profile = forms.ChoiceField(choices=[])
    shipping_profile = forms.ChoiceField(choices=[])


class SubscriptionProfileForm(AuthorizenetContractForm):
    contract_cls = apicontractsv1.customerProfileIdType

    customerProfileId = forms.CharField(max_length=17)
    customerAddressId = forms.CharField(max_length=17)
    customerPaymentProfileId = forms.CharField(max_length=17)
