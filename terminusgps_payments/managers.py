from django.db import models

from terminusgps_payments.models import CustomerProfile


class SubscriptionQuerySet(models.QuerySet):
    def for_customer_profile(
        self, customer_profile: CustomerProfile
    ) -> models.QuerySet:
        return self.filter(customer_profile=customer_profile)


class SubscriptionManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return SubscriptionQuerySet(self.model, using=self._db)
