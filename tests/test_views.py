from django.test import TestCase


class SubscriptionCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/subscriptions/create/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/subscriptions/create/")
        self.assertEqual(response.status_code, 200)

    def test_post_anonymous(self):
        """Fails if a POST request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.post("/subscriptions/create/")
        self.assertEqual(response.status_code, 302)

    def test_post_authenticated(self):
        """Fails if a POST request from an authenticated client returns a response code other than 200."""
        response = self.client.post("/subscriptions/create/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET or non-POST request returns a response code other than 405."""
        response = self.client.put("/subscriptions/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/subscriptions/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/subscriptions/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/subscriptions/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/subscriptions/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/subscriptions/create/")
        self.assertEqual(response.status_code, 405)


class CustomerAddressProfileCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/create/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/address-profiles/create/")
        self.assertEqual(response.status_code, 200)

    def test_post_anonymous(self):
        """Fails if a POST request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.post("/address-profiles/create/")
        self.assertEqual(response.status_code, 302)

    def test_post_authenticated(self):
        """Fails if a POST request from an authenticated client returns a response code other than 200."""
        response = self.client.post("/address-profiles/create/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET or non-POST request returns a response code other than 405."""
        response = self.client.put("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)


class CustomerAddressProfileDetailViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET request returns a response code other than 405."""
        response = self.client.post("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)

    def test_get_authenticated_other(self):
        """Fails if a GET request from another authenticated client returns a response code other than 404."""
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 404)
        self.client.logout()


class CustomerAddressProfileListViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/list/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/address-profiles/list/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            '<a class="hover:underline" href="/address-profiles/1/detail/"><li>TestAddress</li></a>',
            response.rendered_content,
        )
        self.assertNotInHTML(
            '<a class="hover:underline" href="/address-profiles/2/detail/"><li>TestAddress</li></a>',
            response.rendered_content,
        )

    def test_get_authenticated_other(self):
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get("/address-profiles/list/")
        self.assertInHTML(
            '<a class="hover:underline" href="/address-profiles/2/detail/"><li>TestAddress</li></a>',
            response.rendered_content,
        )
        self.assertNotInHTML(
            '<a class="hover:underline" href="/address-profiles/1/detail/"><li>TestAddress</li></a>',
            response.rendered_content,
        )
        self.client.logout()

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET request returns a response code other than 405."""
        response = self.client.post("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)


class CustomerAddressProfileDeleteViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_other(self):
        """Fails if a GET request from another authenticated client returns a response code other than 404."""
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_post_anonymous(self):
        """Fails if a POST request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.post("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 302)

    def test_post_authenticated(self):
        """Fails if a POST request from an authenticated client returns a response code other than 200."""
        response = self.client.post("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET or non-POST request returns a response code other than 405."""
        response = self.client.put("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/address-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)


class CustomerPaymentProfileCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/create/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/payment-profiles/create/")
        self.assertEqual(response.status_code, 200)

    def test_post_anonymous(self):
        """Fails if a POST request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.post("/payment-profiles/create/")
        self.assertEqual(response.status_code, 302)

    def test_post_authenticated(self):
        """Fails if a POST request from an authenticated client returns a response code other than 200."""
        response = self.client.post("/payment-profiles/create/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET or non-POST request returns a response code other than 405."""
        response = self.client.put("/payment-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/payment-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/payment-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/payment-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/payment-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/payment-profiles/create/")
        self.assertEqual(response.status_code, 405)


class CustomerPaymentProfileDetailViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_other(self):
        """Fails if a GET request from another authenticated client returns a response code other than 404."""
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET request returns a response code other than 405."""
        response = self.client.post("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/payment-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)


class CustomerPaymentProfileListViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/payment-profiles/list/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/payment-profiles/list/")
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_other(self):
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get("/payment-profiles/list/")
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET request returns a response code other than 405."""
        response = self.client.post("/payment-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/payment-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/payment-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/payment-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/payment-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/payment-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/payment-profiles/list/")
        self.assertEqual(response.status_code, 405)


class CustomerPaymentProfileDeleteViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_other(self):
        """Fails if a GET request from another authenticated client returns a response code other than 404."""
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_post_anonymous(self):
        """Fails if a POST request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.post("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 302)

    def test_post_authenticated(self):
        """Fails if a POST request from an authenticated client returns a response code other than 200."""
        response = self.client.post("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET or non-POST request returns a response code other than 405."""
        response = self.client.put("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/payment-profiles/1/delete/")
        self.assertEqual(response.status_code, 405)
