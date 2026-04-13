import logging
from collections.abc import Sequence

from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string

from terminusgps_payments.models import Subscription

ACTIVE = Subscription.SubscriptionStatus.ACTIVE
logger = logging.getLogger(__name__)


def send_emails(
    recipient_list: Sequence[str],
    subject: str,
    template_name: str,
    context: dict | None = None,
    html_template_name: str | None = None,
):
    msg = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(template_name, context=context),
        to=recipient_list,
    )
    if html_template_name is not None:
        html_content = render_to_string(html_template_name, context=context)
        msg.attach_alternative(html_content, "text/html")
    return msg.send(fail_silently=True)


@task
def send_subscription_created_email(
    recipient_list: Sequence[str], context: dict | None = None
):
    return send_emails(
        recipient_list=recipient_list,
        subject="Terminus GPS - Subscription Created",
        template_name="terminusgps_payments/emails/subscription_created.txt",
        context=context or {},
        html_template_name="terminusgps_payments/emails/subscription_created.html",
    )


@task
def send_subscription_canceled_email(
    recipient_list: Sequence[str], context: dict | None = None
):
    return send_emails(
        recipient_list=recipient_list,
        subject="Terminus GPS - Subscription Canceled",
        template_name="terminusgps_payments/emails/subscription_canceled.txt",
        context=context or {},
        html_template_name="terminusgps_payments/emails/subscription_canceled.html",
    )
