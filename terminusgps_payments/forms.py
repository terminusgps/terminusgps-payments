from django import forms

from . import fields


class PaymentProfileCreationForm(forms.Form):
    address = fields.AuthorizenetCustomerAddressField()
    credit_card = fields.AuthorizenetCreditCardField()
    create_address_profile = forms.BooleanField(initial=True)
    default = forms.BooleanField(initial=True)


class AddressProfileCreationForm(forms.Form):
    address = fields.AuthorizenetCustomerAddressField()
    default = forms.BooleanField(initial=True)
