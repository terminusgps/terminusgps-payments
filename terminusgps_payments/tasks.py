from django.tasks import task

from .services import sync_customer_profile


@task
def sync_customer_profile_with_authorizenet(pk):
    sync_customer_profile(pk)
