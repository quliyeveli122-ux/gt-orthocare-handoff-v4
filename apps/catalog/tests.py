from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from .models import Category, Product


class StorefrontTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", assets="/nonexistent", verbosity=0)

    def test_seed_counts(self):
        self.assertEqual(Category.objects.count(), 7)
        self.assertEqual(Product.objects.count(), 33)

    def test_home(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "ორთოპედიული ფიქსატორები")  # hero
        self.assertContains(r, "მოთხოვნადი პროდუქტები")     # featured block
        self.assertContains(r, "ტრავმატოლოგი ზარზე")        # on-call service strip
        self.assertContains(r, "რენტგენოლოგიური კვლევა ბინაზე გამოძახებით")  # x-ray strip

    def test_shop_lists_all(self):
        r = self.client.get("/shop/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["page"].paginator.count, 33)

    def test_category_filter(self):
        r = self.client.get("/shop/knee/")
        self.assertEqual(r.context["page"].paginator.count, 7)
        self.assertContains(r, "M-02")

    def test_search_by_code(self):
        r = self.client.get("/shop/", {"q": "M-02"})
        self.assertEqual(r.context["page"].paginator.count, 1)

    def test_search_by_name(self):
        r = self.client.get("/shop/", {"q": "Walker"})
        self.assertContains(r, "K-03")

    def test_no_prices_on_storefront(self):
        # call-to-order catalog: the ₾ price symbol must not appear anywhere public
        for url in ["/", "/shop/", "/shop/knee/",
                    Product.objects.get(code="M-02").get_absolute_url()]:
            self.assertNotContains(self.client.get(url), "₾", msg_prefix=url)

    def test_call_to_order_present(self):
        # product page shows a tel: call-to-order button, no add-to-cart form
        r = self.client.get(Product.objects.get(code="M-02").get_absolute_url())
        self.assertContains(r, "tel:")
        self.assertContains(r, "დარეკეთ შესაკვეთად")
        self.assertNotContains(r, "add-cart")

    def test_cart_urls_removed(self):
        self.assertEqual(self.client.get("/cart/").status_code, 404)
        self.assertEqual(self.client.get("/cart/checkout/").status_code, 404)

    def test_every_product_page_renders(self):
        # includes products with empty sizes (KN-04, P-01, crutches) — regression
        for p in Product.objects.all():
            r = self.client.get(p.get_absolute_url())
            self.assertEqual(r.status_code, 200, p.code)

    def test_product_detail(self):
        p = Product.objects.get(code="M-02")
        r = self.client.get(p.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "M-02")
        self.assertContains(r, "მუხლის სახსრიანი ორთეზი")

    def test_language_switch(self):
        self.client.get("/set-lang/en/")
        r = self.client.get("/")
        self.assertContains(r, "Orthopedic braces")
        p = Product.objects.get(code="M-02")
        r = self.client.get(p.get_absolute_url())
        self.assertContains(r, "Hinged Knee Brace")

    def test_healthz(self):
        self.assertEqual(self.client.get("/healthz").json()["status"], "ok")

    def test_phones_editable_via_site_settings(self):
        from apps.content.models import SiteSettings
        s = SiteSettings.load()
        s.phone_trauma = "+995 500 00 00 01"
        s.save()
        r = self.client.get("/")
        self.assertContains(r, "+995 500 00 00 01")


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", assets="/nonexistent", verbosity=0)
        cls.admin = User.objects.create_superuser("boss", "boss@gt.ge", "pass12345")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_dashboard_renders(self):
        r = self.client.get("/admin/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "ახალი შეტყობინება")   # leads KPI card
        self.assertContains(r, "ordersChart")         # chart canvas

    def test_product_changelist_and_form(self):
        r = self.client.get("/admin/catalog/product/")
        self.assertEqual(r.status_code, 200)
        p = Product.objects.first()
        r = self.client.get(f"/admin/catalog/product/{p.pk}/change/")
        self.assertEqual(r.status_code, 200)

    def test_product_saves_without_price(self):
        # price is optional now — creating a product with no price must work
        cat = Category.objects.first()
        p = Product.objects.create(code="ZZ-99", slug="zz-99", name_ka="ტესტი",
                                   category=cat, image="products/M-02.jpg")
        self.assertIsNone(p.price)

    def test_content_changelists(self):
        for url in ["/admin/content/banner/", "/admin/content/blogpost/",
                    "/admin/content/storelocation/", "/admin/content/faq/",
                    "/admin/content/contactmessage/", "/admin/content/sitesettings/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
