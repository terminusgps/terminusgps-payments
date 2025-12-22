import datetime

from authorizenet import apicontractsv1
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.constants import BankAccountType

WIDGET_CSS_CLASS = getattr(
    settings,
    "WIDGET_CSS_CLASS",
    "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
)


class AddressField(forms.MultiValueField):
    def __init__(self, *args, **kwargs) -> None:
        fields = (
            forms.CharField(max_length=50),
            forms.CharField(max_length=50),
            forms.CharField(max_length=60),
            forms.CharField(max_length=40),
            forms.CharField(max_length=50),
            forms.CharField(max_length=60),
            forms.CharField(max_length=20),
            forms.CharField(max_length=25),
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
            return addr
        return None


class AddressWidget(forms.MultiWidget):
    template_name = "terminusgps_payments/widgets/address.html"
    default_widgets = {
        "first_name": forms.widgets.TextInput(
            attrs={"maxlength": "50", "placeholder": "First"}
        ),
        "last_name": forms.widgets.TextInput(
            attrs={"maxlength": "50", "placeholder": "Last"}
        ),
        "street": forms.widgets.TextInput(
            attrs={"maxlength": "60", "placeholder": "Street"}
        ),
        "city": forms.widgets.TextInput(
            attrs={"maxlength": "40", "placeholder": "City"}
        ),
        "state": forms.widgets.TextInput(
            attrs={"maxlength": "50", "placeholder": "State"}
        ),
        "country": forms.widgets.TextInput(
            attrs={"maxlength": "60", "placeholder": "Country"}
        ),
        "zip": forms.widgets.TextInput(
            attrs={"maxlength": "20", "placeholder": "ZIP #"}
        ),
        "phone": forms.widgets.TextInput(
            attrs={"maxlength": "25", "placeholder": "Phone #"}
        ),
    }

    def __init__(self, widgets=None, attrs=None) -> None:
        if attrs is None:
            attrs = {
                "autocomplete": "on",
                "class": WIDGET_CSS_CLASS,
                "enterkeyhint": "next",
                "inputmode": "text",
            }
        return super().__init__(
            widgets=widgets
            if widgets is not None
            else self.default_widgets.copy(),
            attrs=attrs,
        )

    def decompress(self, value):
        if value:
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
        return [None, None, None, None, None, None, None, None]


class BankAccountField(forms.MultiValueField):
    def __init__(self, *args, **kwargs) -> None:
        fields = (
            forms.CharField(max_length=9),
            forms.CharField(max_length=17),
            forms.CharField(max_length=22),
            forms.CharField(max_length=50),
            forms.ChoiceField(
                choices=BankAccountType.choices,
                initial=BankAccountType.CHECKING,
            ),
        )
        super().__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if all(data_list):
            ba = apicontractsv1.bankAccountType()
            ba.routingNumber = str(data_list[0])
            ba.accountNumber = str(data_list[1])
            ba.nameOnAccount = str(data_list[2])
            ba.bankName = str(data_list[3])
            ba.accountType = str(data_list[4])
            ba.echeckType = "PPD"
            return ba
        return None


class BankAccountWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_payments/widgets/bank_account.html"
    default_widgets = {
        "routing_number": forms.widgets.TextInput(
            attrs={"placeholder": "Routing #", "maxlength": "9"}
        ),
        "number": forms.widgets.TextInput(
            attrs={"placeholder": "Account #", "maxlength": "17"}
        ),
        "name": forms.widgets.TextInput(
            attrs={"placeholder": "Owner Name", "maxlength": "22"}
        ),
        "bank": forms.widgets.TextInput(
            attrs={"placeholder": "Bank Name", "maxlength": "50"}
        ),
        "type": forms.widgets.Select(choices=BankAccountType.choices),
    }

    def __init__(self, widgets=None, attrs=None) -> None:
        if attrs is None:
            attrs = {
                "autocomplete": "off",
                "autocorrect": "off",
                "class": WIDGET_CSS_CLASS,
                "enterkeyhint": "next",
            }
        return super().__init__(
            widgets=widgets
            if widgets is not None
            else self.default_widgets.copy(),
            attrs=attrs,
        )

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
            forms.CharField(min_length=15, max_length=19),
            forms.DateField(input_formats=["%m", "%-m"]),
            forms.DateField(input_formats=["%y"]),
            forms.CharField(min_length=3, max_length=4),
        )
        super().__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if all(data_list):
            expiry = datetime.date(
                month=data_list[1].month, year=data_list[2].year, day=1
            )
            cc = apicontractsv1.creditCardType()
            cc.cardNumber = str(data_list[0])
            cc.cardCode = str(data_list[3])
            cc.expirationDate = expiry.strftime("%Y-%m")
            return cc
        return None


class CreditCardWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_payments/widgets/credit_card.html"
    default_widgets = {
        "number": forms.widgets.TextInput(
            attrs={
                "maxlength": "19",
                "minlength": "15",
                "placeholder": "Card #",
            }
        ),
        "expiry_month": forms.widgets.TextInput(
            attrs={"maxlength": "2", "minlength": "1", "placeholder": "MM"}
        ),
        "expiry_year": forms.widgets.TextInput(
            attrs={"maxlength": "2", "minlength": "2", "placeholder": "YY"}
        ),
        "ccv": forms.widgets.TextInput(
            attrs={"maxlength": "4", "minlength": "3", "placeholder": "CCV #"}
        ),
    }

    def __init__(self, widgets=None, attrs=None) -> None:
        if attrs is None:
            attrs = {
                "autocomplete": "off",
                "autocorrect": "off",
                "class": WIDGET_CSS_CLASS,
                "enterkeyhint": "next",
                "inputmode": "numeric",
            }
        super().__init__(
            widgets=widgets
            if widgets is not None
            else self.default_widgets.copy(),
            attrs=attrs,
        )

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
    address = AddressField(label=_("Billing Address"), widget=AddressWidget())
    credit_card = CreditCardField(
        label=_("Credit Card"), widget=CreditCardWidget()
    )
    default = forms.BooleanField(
        initial=True, label=_("Set payment profile as default?")
    )


class CustomerPaymentProfileBankAccountCreateForm(forms.Form):
    address = AddressField(label=_("Billing Address"), widget=AddressWidget())
    bank_account = BankAccountField(
        label=_("Bank Account"), widget=BankAccountWidget()
    )
    default = forms.BooleanField(
        initial=True, label=_("Set payment profile as default?")
    )


class CustomerAddressProfileCreateForm(forms.Form):
    address = AddressField(label=_("Shipping Address"), widget=AddressWidget())
    default = forms.BooleanField(
        initial=True, label=_("Set address profile as default?")
    )
