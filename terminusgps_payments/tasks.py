import logging
from collections.abc import Sequence

from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.tasks import task
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetError,
    AuthorizenetService,
)

from terminusgps_payments.models import Subscription

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


@task
@transaction.atomic
def refresh_subscription_status(pk: int) -> None:
    try:
        subscription = Subscription.objects.get(pk=pk)
    except Subscription.DoesNotExist:
        msg = f"Failed to retrieve subscription #{pk} from db"
        logger.critical(msg)
        return
    try:
        response = AuthorizenetService().execute(
            api.get_subscription(subscription_id=pk)
        )
    except AuthorizenetError as error:
        logger.warning(error)
        return

    updated_fields = ["status"]
    if response.subscription.status == Subscription.SubscriptionStatus.EXPIRED:
        start_date_str = str(response.subscription.paymentSchedule.startDate)
        start_date = parse_date(start_date_str)
        updated_fields.append("expires_on")
    subscription.status = response.subscription.status
    subscription.save(update_fields=updated_fields)
    return
