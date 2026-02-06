from django.test import RequestFactory, TestCase
from django.views.generic import TemplateView

from terminusgps_payments.mixins import HtmxTemplateResponseMixin


class TestTemplateView(HtmxTemplateResponseMixin, TemplateView):
    pass


class HtmxTemplateResponseMixinTestCase(TestCase):
    def setUp(self):
        self.view = TestTemplateView(template_name="test.html")

    def test_render_to_response_explicit_partial_name(self):
        """Fails if :py:attr:`template_name` wasn't set to an explicitly provided :py:attr:`partial_name`."""
        headers = {"HX-Request": "true"}
        request = RequestFactory().get("/", headers=headers)
        explicit_partial_name = "test.html#mypartial"
        self.view.partial_name = explicit_partial_name
        self.view.setup(request)
        self.view.render_to_response(context=self.view.get_context_data())
        self.assertEqual(explicit_partial_name, self.view.template_name)

    def test_render_to_response_htmx_request(self):
        """Fails if :py:attr:`template_name` wasn't updated on an htmx request."""
        headers = {"HX-Request": "true"}
        request = RequestFactory().get("/", headers=headers)
        self.view.setup(request)
        self.view.render_to_response(context=self.view.get_context_data())
        self.assertEqual("test.html#main", self.view.template_name)

    def test_render_to_response_htmx_request_boosted(self):
        """Fails if :py:attr:`template_name` was updated on a boosted htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        request = RequestFactory().get("/", headers=headers)
        self.view.setup(request)
        self.view.render_to_response(context=self.view.get_context_data())
        self.assertEqual("test.html", self.view.template_name)

    def test_render_to_response_non_htmx_request(self):
        """Fails if :py:attr:`template_name` was updated on a non-htmx request."""
        headers = {}
        request = RequestFactory().get("/", headers=headers)
        self.view.setup(request)
        self.view.render_to_response(context=self.view.get_context_data())
        self.assertEqual("test.html", self.view.template_name)
