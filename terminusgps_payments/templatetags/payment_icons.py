from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def credit_card_icon(value):
    match value.lower():
        case "visa":
            return "terminusgps_payments/icons/visa.svg"
        case _:
            return "terminusgps_payments/icons/unknown.svg"
