from django.tasks import task

from .services import sync_customer_profile as sync_with_authorizenet


@task
def sync_customer_profile(pk):
    sync_with_authorizenet(pk)
