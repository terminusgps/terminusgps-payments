from django.test import RequestFactory, TestCase
from django.views.generic import TemplateView

from terminusgps_payments.mixins import (
    AuthorizenetMultipleObjectMixin,
    AuthorizenetSingleObjectMixin,
    HtmxTemplateResponseMixin,
)
from terminusgps_payments.models import CustomerAddressProfile


class HtmxTemplateResponseMixinTestView(
    HtmxTemplateResponseMixin, TemplateView
):
    template_name = "terminusgps_payments/tests/htmxtemplateresponsemixin.html"


class AuthorizenetSingleObjectMixinTestView(AuthorizenetSingleObjectMixin):
    model = CustomerAddressProfile


class AuthorizenetMultipleObjectMixinTestView(AuthorizenetMultipleObjectMixin):
    model = CustomerAddressProfile


class HtmxTemplateResponseMixinTestCase(TestCase):
    def setUp(self):
        self.view_cls = HtmxTemplateResponseMixinTestView

    def test_render_to_response_htmx_request(self):
        """Fails if :py:attr:`template_name` wasn't updated on an htmx request."""
        headers = {"HX-Request": "true"}
        request = RequestFactory().get("/", headers=headers)
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(context=view.get_context_data())
        self.assertIn("#content", view.template_name)

    def test_render_to_response_htmx_request_boosted(self):
        """Fails if :py:attr:`template_name` was updated on a boosted htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        request = RequestFactory().get("/", headers=headers)
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(context=view.get_context_data())
        self.assertNotIn("#content", view.template_name)

    def test_render_to_response_no_htmx_request(self):
        """Fails if :py:attr:`template_name` was updated on a non-htmx request."""
        headers = {}
        request = RequestFactory().get("/", headers=headers)
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(context=view.get_context_data())
        self.assertNotIn("#content", view.template_name)


class AuthorizenetSingleObjectMixinTestCase(TestCase):
    def setUp(self):
        self.view_cls = AuthorizenetSingleObjectMixinTestView

    def test_get_queryset(self):
        """Fails if :py:meth:`get_queryset` returns another user's Authorizenet profiles."""
