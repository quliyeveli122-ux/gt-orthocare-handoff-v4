from django.test import TestCase

from apps.content.models import ContactMessage

# The online cart/checkout flow was retired in favour of a call-to-order catalog.
# The Order/OrderItem models are kept for optional internal use but are no longer
# reachable from the storefront. Contact messages are now the lead channel.


class ContactTests(TestCase):
    def test_contact_form_creates_message(self):
        r = self.client.post("/contact/", {
            "name": "ნინო", "phone": "+995 577 55 66 77",
            "message": "გამარჯობა", "next": "/contact/",
        })
        self.assertRedirects(r, "/contact/")
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_cart_and_checkout_are_gone(self):
        for url in ["/cart/", "/cart/add/", "/cart/checkout/", "/cart/success/"]:
            self.assertEqual(self.client.get(url).status_code, 404, url)
