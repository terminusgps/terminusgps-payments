from django.db import models


class UserExclusiveQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(customer_profile__user=user)


class UserExclusiveManager(models.Manager):
    def get_queryset(self):
        return UserExclusiveQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)
