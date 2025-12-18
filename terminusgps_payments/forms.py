import datetime

from authorizenet import apicontractsv1
from django import forms
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.constants import BankAccountType


class AddressField(forms.MultiValueField):
    def __init__(self, *args, **kwargs) -> None:
        fields = (
            forms.CharField(
                label=_("First Name"),
                max_length=50,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "First"}
                ),
            ),
            forms.CharField(
                label=_("Last Name"),
                max_length=50,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "Last"}
                ),
            ),
            forms.CharField(
                label=_("Street"),
                max_length=60,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "17610 South Dr"}
                ),
            ),
            forms.CharField(
                label=_("City"),
                max_length=40,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "Cypress"}
                ),
            ),
            forms.CharField(
                label=_("State"),
                max_length=50,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "Texas"}
                ),
            ),
            forms.CharField(
                label=_("Country"),
                max_length=60,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "USA"}
                ),
            ),
            forms.CharField(
                label=_("ZIP #"),
                max_length=20,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "77433"}
                ),
            ),
            forms.CharField(
                label=_("Phone #"),
                max_length=25,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "+17139045262"}
                ),
            ),
        )
        super().__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if all(data_list):
            addr = apicontractsv1.customerAddressType()
            addr.firstName = str(data_list[0])
            addr.lastName = str(data_list[1])
            addr.address = str(data_list[2])
            addr.city = str(data_list[3])
            addr.state = str(data_list[4])
            addr.country = str(data_list[5])
            addr.zip = str(data_list[6])
            addr.phoneNumber = str(data_list[7])
        return [None, None, None, None, None, None, None, None]


class AddressWidget(forms.MultiWidget):
    template_name = "terminusgps_payments/widgets/address.html"

    def decompress(self, value):
        if value is None:
            return None
        return [
            str(value.firstName),
            str(value.lastName),
            str(value.address),
            str(value.city),
            str(value.state),
            str(value.country),
            str(value.zip),
            str(value.phoneNumber),
        ]


class BankAccountField(forms.MultiValueField):
    def __init__(self, *args, **kwargs) -> None:
        fields = (
            forms.ChoiceField(
                label=_("Account Type"),
                choices=BankAccountType.choices,
                initial=BankAccountType.CHECKING,
                widget=forms.widgets.Select(attrs={"class": "peer"}),
            ),
            forms.CharField(
                label=_("Routing #"),
                max_length=9,
                widget=forms.widgets.NumberInput(
                    attrs={"class": "peer", "placeholder": "X" * 9}
                ),
            ),
            forms.CharField(
                label=_("Account #"),
                max_length=17,
                widget=forms.widgets.NumberInput(
                    attrs={"class": "peer", "placeholder": "X" * 17}
                ),
            ),
            forms.CharField(
                label=_("Account Name"),
                max_length=22,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "Terminus GPS"}
                ),
            ),
            forms.CharField(
                label=_("Bank Name"),
                max_length=50,
                widget=forms.widgets.TextInput(
                    attrs={"class": "peer", "placeholder": "Wells Fargo"}
                ),
            ),
        )
        super().__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if all(data_list):
            ba = apicontractsv1.bankAccountType()
            ba.accountType = str(data_list[0])
            ba.routingNumber = str(data_list[1])
            ba.accountNumber = str(data_list[2])
            ba.nameOnAccount = str(data_list[3])
            ba.bankName = str(data_list[4])
            ba.echeckType = "PPD"
            return ba
        return


class BankAccountWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_payments/widgets/bank_account.html"

    def decompress(self, value):
        if value:
            return [
                str(value.accountType),
                str(value.routingNumber),
                str(value.accountNumber),
                str(value.nameOnAccount),
                str(value.bankName),
            ]
        return [None, None, None, None, None]


class CreditCardField(forms.MultiValueField):
    def __init__(self, *args, **kwargs) -> None:
        fields = (
            forms.CharField(
                label=_("Card #"),
                max_length=19,
                min_length=15,
                widget=forms.widgets.NumberInput(
                    attrs={"class": "peer", "placeholder": "X" * 16}
                ),
            ),
            forms.DateField(
                input_formats=["%m", "%-m"],
                label=_("Expiration Month"),
                widget=forms.widgets.NumberInput(
                    attrs={"class": "peer", "placeholder": "MM"}
                ),
            ),
            forms.DateField(
                input_formats=["%y"],
                label=_("Expiration Year"),
                widget=forms.widgets.NumberInput(
                    attrs={"class": "peer", "placeholder": "YY"}
                ),
            ),
            forms.CharField(
                label=_("CCV #"),
                max_length=4,
                min_length=3,
                widget=forms.widgets.NumberInput(
                    attrs={"class": "peer", "placeholder": "X" * 3}
                ),
            ),
        )
        super().__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if all(data_list):
            expiry = datetime.date(
                month=data_list[1], year=data_list[2], day=1
            )

            cc = apicontractsv1.creditCardType()
            cc.cardNumber = str(data_list[0])
            cc.cardCode = str(data_list[3])
            cc.expirationDate = expiry.strftime("%Y-%m")
            return cc
        return


class CreditCardWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_payments/widgets/credit_card.html"

    def decompress(self, value):
        if value:
            expiry = datetime.datetime.strptime(
                str(value.expirationDate), "%Y-%m"
            )
            return [
                str(value.cardNumber),
                expiry.strftime("%m"),
                expiry.strftime("%y"),
                str(value.cardCode),
            ]
        return [None, None, None, None]


class CustomerPaymentProfileCreditCardCreateForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        if "instance" in kwargs:
            kwargs.pop("instance")
        super().__init__(*args, **kwargs)

    credit_card = CreditCardField()
    address = AddressField()
    default = forms.BooleanField(initial=True)


class CustomerPaymentProfileBankAccountCreateForm(forms.Form):
    bank_account = BankAccountField()
    address = AddressField()
    default = forms.BooleanField(initial=True)
