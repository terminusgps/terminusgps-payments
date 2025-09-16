from authorizenet import apicontractsv1
from django import forms
from django.utils import timezone

__all__ = ["PaymentProfileCreationForm", "AddressProfileCreationForm"]


class AuthorizenetCustomerAddressWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_payments/widgets/address.html"

    def decompress(self, value) -> list[str | None]:
        if value:
            return [
                str(value.firstName),
                str(value.lastName),
                str(value.phoneNumber),
                str(value.address),
                str(value.city),
                str(value.state),
                str(value.zip),
                str(value.country),
            ]
        return [None, None, None, None, None, None, None, None]


class AuthorizenetCustomerAddressField(forms.MultiValueField):
    def __init__(self, **kwargs) -> None:
        error_messages = {}
        fields = (
            forms.CharField(label="First Name"),
            forms.CharField(label="Last Name"),
            forms.CharField(label="Phone #"),
            forms.CharField(label="Street"),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Zip #"),
            forms.CharField(label="Country"),
        )
        widget = AuthorizenetCustomerAddressWidget(
            widgets={
                "first_name": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "First",
                        "minlength": "1",
                        "maxlength": "24",
                        "inputmode": "text",
                        "enterkeyhint": "next",
                    }
                ),
                "last_name": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "Last",
                        "minlength": "1",
                        "maxlength": "24",
                        "inputmode": "text",
                        "enterkeyhint": "next",
                    }
                ),
                "phone_number": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "+17139045262",
                        "minlength": "12",
                        "maxlength": "16",
                        "inputmode": "tel",
                        "enterkeyhint": "next",
                    }
                ),
                "street": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "17610 South Dr",
                        "minlength": "4",
                        "maxlength": "64",
                        "inputmode": "text",
                        "enterkeyhint": "next",
                    }
                ),
                "city": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "Cypress",
                        "minlength": "4",
                        "maxlength": "64",
                        "inputmode": "text",
                        "enterkeyhint": "next",
                    }
                ),
                "state": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "Texas",
                        "minlength": "4",
                        "maxlength": "64",
                        "inputmode": "text",
                        "enterkeyhint": "next",
                    }
                ),
                "zip": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "77433",
                        "minlength": "5",
                        "maxlength": "9",
                        "inputmode": "numeric",
                        "enterkeyhint": "next",
                    }
                ),
                "country": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white w-full",
                        "placeholder": "USA",
                        "minlength": "3",
                        "maxlength": "64",
                        "inputmode": "text",
                        "enterkeyhint": "done",
                    }
                ),
            }
        )
        super().__init__(
            error_messages=error_messages,
            fields=fields,
            widget=widget,
            require_all_fields=True,
            **kwargs,
        )

    def compress(self, data_list) -> apicontractsv1.customerAddressType:
        return apicontractsv1.customerAddressType(
            firstName=data_list[0],
            lastName=data_list[1],
            phoneNumber=data_list[2],
            address=data_list[3],
            city=data_list[4],
            state=data_list[5],
            zip=data_list[6],
            country=data_list[7],
        )


class AuthorizenetCreditCardWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_payments/widgets/credit_card.html"

    def decompress(self, value) -> list[str | None]:
        if value:
            year, month = str(value.expirationDate).split("-")
            return [
                str(value.cardNumber),
                month,
                year[-2:],
                str(value.cardCode),
            ]
        return [None, None, None, None]


class AuthorizenetCreditCardField(forms.MultiValueField):
    def __init__(self, **kwargs) -> None:
        error_messages = {}
        fields = (
            forms.CharField(label="Card #"),
            forms.IntegerField(label="Expiry Month"),
            forms.IntegerField(label="Expiry Year"),
            forms.CharField(label="CCV #"),
        )
        widget = AuthorizenetCreditCardWidget(
            widgets={
                "number": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white col-span-2",
                        "placeholder": "4111111111111111",
                        "minlength": "16",
                        "maxlength": "19",
                        "inputmode": "numeric",
                        "enterkeyhint": "next",
                    }
                ),
                "expiry_month": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white",
                        "placeholder": "MM",
                        "min": 1,
                        "max": 12,
                        "minlength": "2",
                        "maxlength": "2",
                        "inputmode": "numeric",
                        "enterkeyhint": "next",
                    }
                ),
                "expiry_year": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white",
                        "placeholder": "YY",
                        "min": int(str(timezone.now().year)[-2:]),
                        "max": 99,
                        "minlength": "2",
                        "maxlength": "2",
                        "inputmode": "numeric",
                        "enterkeyhint": "next",
                    }
                ),
                "ccv": forms.widgets.TextInput(
                    attrs={
                        "class": "p-2 rounded border bg-white col-span-2",
                        "placeholder": "444",
                    }
                ),
            }
        )

        super().__init__(
            error_messages=error_messages,
            fields=fields,
            widget=widget,
            require_all_fields=True,
            **kwargs,
        )

    def compress(self, data_list) -> apicontractsv1.creditCardType:
        return apicontractsv1.creditCardType(
            cardNumber=data_list[0],
            expirationDate=f"{data_list[2] + 2000}-{data_list[1]:02}",
            cardCode=data_list[3],
        )


class PaymentProfileCreationForm(forms.Form):
    address = AuthorizenetCustomerAddressField()
    credit_card = AuthorizenetCreditCardField()
    default = forms.BooleanField(
        initial=True,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700 select-none"}
        ),
    )


class AddressProfileCreationForm(forms.Form):
    address = AuthorizenetCustomerAddressField()
    default = forms.BooleanField(
        initial=True,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700 select-none"}
        ),
    )
