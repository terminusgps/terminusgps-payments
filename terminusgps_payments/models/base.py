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
        service = AuthorizenetService()
        if self.pk and not kwargs.pop("push", False):
            logger.debug(f"Syncing #{self.pk} with Authorizenet...")
            self.sync(service)
        else:
            logger.debug(f"Pushing #{self.pk} to Authorizenet...")
            resp = self.push(service)
            if not self.pk:
                self.pk = self._extract_id(resp)
                logger.debug(f"Created #{self.pk} in Authorizenet...")
        return super().save(**kwargs)

    @abc.abstractmethod
    def _extract_id(self, elem: ObjectifiedElement) -> int:
        raise NotImplementedError("Subclasses must implement this method.")

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
    def sync(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> None:
        raise NotImplementedError("Subclasses must implement this method.")
