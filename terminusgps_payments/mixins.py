from django.db.models import QuerySet
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin


class HtmxTemplateResponseMixin(TemplateResponseMixin):
    def render_to_response(self, context, **response_kwargs):
        htmx_request = bool(self.request.headers.get("HX-Request"))
        boosted = bool(self.request.headers.get("HX-Boosted"))
        if htmx_request and not boosted:
            self.template_name = f"{self.template_name}#content"
        return super().render_to_response(context, **response_kwargs)


class AuthorizenetSingleObjectMixin(SingleObjectMixin):
    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


class AuthorizenetMultipleObjectMixin(MultipleObjectMixin):
    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        ).order_by(self.get_ordering())
