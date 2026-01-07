import abc

from django.db import models
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet.service import AuthorizenetService


class AuthorizenetModel(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, blank=True, editable=False
    )
    """Authorizenet object id."""

    class Meta:
        abstract = True

    def save(self, **kwargs) -> None:
        """Creates or updates the object in Authorizenet before saving."""
        service = AuthorizenetService()
        if not self.pk:
            self.id = self.create_in_authorizenet(service)
        elif kwargs.pop("push", True):
            self.update_in_authorizenet(service)
        else:
            self.sync_with_authorizenet(service)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the object in Authorizenet before deleting it locally."""
        if not self.pk:
            return super().delete(*args, **kwargs)
        service = AuthorizenetService()
        self.delete_in_authorizenet(service)
        return super().delete(*args, **kwargs)

    @abc.abstractmethod
    def create_in_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> int:
        """Tries to create the object in Authorizenet and return its id."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> ObjectifiedElement:
        """Tries to retrieve fresh object data from Authorizenet and return it."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def update_in_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> None:
        """Tries to update the object in Authorizenet."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def delete_in_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> None:
        """Tries to delete the object in Authorizenet."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def sync_with_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> None:
        """Tries to sync the object's local data with Authorizenet's remote data."""
        raise NotImplementedError("Subclasses must implement this method.")
