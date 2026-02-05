import abc
import logging

from django.db import models
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet.service import AuthorizenetService

logger = logging.getLogger(__name__)


class AuthorizenetModel(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True, blank=True)
    """Authorizenet object id."""

    class Meta:
        abstract = True

    def save(self, **kwargs) -> None:
        service = kwargs.pop("service", AuthorizenetService())
        ref = kwargs.pop("reference_id", None)
        if not kwargs.pop("push", False) and self.pk:
            logger.debug(f"Syncing #{self.pk} with Authorizenet...")
            elem = self.pull(service, reference_id=ref)
            self.sync(elem)
            logger.debug(f"Synced #{self.pk} with Authorizenet.")
        else:
            resp = self.push(service, reference_id=ref)
            if not self.pk:
                self.pk = self._extract_authorizenet_id(resp)
            logger.debug(f"Pushed #{self.pk} to Authorizenet.")
        return super().save(**kwargs)

    @abc.abstractmethod
    def push(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> ObjectifiedElement:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> ObjectifiedElement:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def sync(self, elem: ObjectifiedElement, **kwargs) -> None:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def _delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        raise NotImplementedError("Subclasses must implement this method.")
