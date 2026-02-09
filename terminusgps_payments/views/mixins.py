from django.db.models import QuerySet
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin


class HtmxTemplateResponseMixin(TemplateResponseMixin):
    partial_name: str | None = None

    def render_to_response(self, context, **response_kwargs):
        htmx_request = bool(self.request.headers.get("HX-Request"))
        boosted = bool(self.request.headers.get("HX-Boosted"))
        if htmx_request and not boosted:
            if not self.partial_name:
                self.partial_name = f"{self.template_name}#main"
            self.template_name = self.partial_name
        return super().render_to_response(context, **response_kwargs)


class AuthorizenetSingleObjectMixin(SingleObjectMixin):
    def get_queryset(self) -> QuerySet:
        if hasattr(self.request, "user"):
            return self.model.objects.filter(
                customer_profile__user=self.request.user
            )
        return self.model.objects.none()


class AuthorizenetMultipleObjectMixin(MultipleObjectMixin):
    def get_queryset(self) -> QuerySet:
        if hasattr(self.request, "user"):
            return self.model.objects.filter(
                customer_profile__user=self.request.user
            ).order_by(self.get_ordering())
        return self.model.objects.none()
