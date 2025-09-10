from authorizenet import apicontractsv1
from django import forms
from django.utils import timezone
from terminusgps.validators import validate_e164_phone_number

__all__ = ["PaymentProfileCreationForm", "AddressProfileCreationForm"]


def get_field_attrs(fields: tuple) -> list[dict[str, str]]:
    # TODO: Get more attributes from fields
    field_attrs = []
    for field in fields:
        attrs = {}
        if hasattr(field, "min_length") and field.min_length:
            attrs["minlength"] = field.min_length
        if hasattr(field, "max_length") and field.max_length:
            attrs["maxlength"] = field.min_length
        field_attrs.append(attrs)
    return field_attrs


class AuthorizenetCustomerAddressWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_payments/widgets/address.html"

    def __init__(self, attrs=None, field_attrs=None) -> None:
        if attrs is None:
            attrs = {}
        if field_attrs is None:
            field_attrs = [{} for _ in range(8)]
        widgets = {
            "first_name": forms.widgets.TextInput(
                attrs=attrs | field_attrs[0] | {"placeholder": "First Name"}
            ),
            "last_name": forms.widgets.TextInput(
                attrs=attrs | field_attrs[1] | {"placeholder": "Last Name"}
            ),
            "phone_number": forms.widgets.TextInput(
                attrs=attrs | field_attrs[2] | {"placeholder": "+17139045262"}
            ),
            "street": forms.widgets.TextInput(
                attrs=attrs
                | field_attrs[3]
                | {"placeholder": "17610 South Dr"}
            ),
            "city": forms.widgets.TextInput(
                attrs=attrs | field_attrs[4] | {"placeholder": "Houston"}
            ),
            "state": forms.widgets.TextInput(
                attrs=attrs | field_attrs[5] | {"placeholder": "Texas"}
            ),
            "zip": forms.widgets.TextInput(
                attrs=attrs | field_attrs[6] | {"placeholder": "77433"}
            ),
            "country": forms.widgets.TextInput(
                attrs=attrs | field_attrs[7] | {"placeholder": "USA"}
            ),
        }
        super().__init__(widgets=widgets, attrs=attrs)

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
            forms.CharField(label="First Name", min_length=4, max_length=16),
            forms.CharField(label="Last Name", min_length=4, max_length=16),
            forms.CharField(
                label="Phone #", validators=[validate_e164_phone_number]
            ),
            forms.CharField(label="Street", min_length=4, max_length=64),
            forms.CharField(label="City", min_length=4, max_length=64),
            forms.CharField(label="State", min_length=4, max_length=64),
            forms.CharField(label="Zip #", min_length=5, max_length=10),
            forms.CharField(label="Country", min_length=2, max_length=16),
        )
        widget = AuthorizenetCustomerAddressWidget(
            attrs={
                "class": "p-2 rounded border border-current w-full text-gray-800 bg-gray-50 dark:text-gray-100 dark:bg-gray-400 group-has-[.errorlist]:text-red-600 group-has-[.errorlist]:bg-red-100"
            },
            field_attrs=get_field_attrs(fields),
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

    def __init__(self, attrs=None, field_attrs=None) -> None:
        if attrs is None:
            attrs = {}
        if field_attrs is None:
            field_attrs = [{} for _ in range(3)]
        now = timezone.now()
        widgets = {
            "number": forms.widgets.TextInput(
                attrs=attrs
                | field_attrs[0]
                | {"placeholder": "4111111111111111"}
            ),
            "expiry_month": forms.widgets.TextInput(
                attrs=attrs
                | field_attrs[1]
                | {"placeholder": now.strftime("%m")}
            ),
            "expiry_year": forms.widgets.TextInput(
                attrs=attrs
                | field_attrs[2]
                | {"placeholder": now.strftime("%y")}
            ),
            "ccv": forms.widgets.TextInput(
                attrs=attrs | field_attrs[3] | {"placeholder": "444"}
            ),
        }
        super().__init__(widgets=widgets, attrs=attrs)

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
        current_year = int(str(timezone.now().year)[-2:])
        fields = (
            forms.CharField(label="Card #", min_length=16),
            forms.IntegerField(
                label="Expiry Month", min_value=1, max_value=12
            ),
            forms.IntegerField(
                label="Expiry Year", min_value=current_year, max_value=99
            ),
            forms.CharField(label="CCV #", min_length=3, max_length=4),
        )
        widget = AuthorizenetCreditCardWidget(
            attrs={
                "class": "p-2 rounded border border-current w-full text-gray-800 bg-gray-50 dark:text-gray-100 dark:bg-gray-400 group-has-[.errorlist]:text-red-600 group-has-[.errorlist]:bg-red-100"
            },
            field_attrs=get_field_attrs(fields),
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
    create_address_profile = forms.BooleanField(initial=True)
    default = forms.BooleanField(initial=True)


class AddressProfileCreationForm(forms.Form):
    address = AuthorizenetCustomerAddressField()
    default = forms.BooleanField(initial=True)
