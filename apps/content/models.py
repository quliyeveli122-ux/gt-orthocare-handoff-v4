from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import TranslatableMixin


class Banner(TranslatableMixin, models.Model):
    title_ka = models.CharField("სათაური (ქართ.)", max_length=200, blank=True)
    title_en = models.CharField("Title (EN)", max_length=200, blank=True)
    image = models.ImageField(
        "ბანერი / Banner image", upload_to="banners/",
        help_text="Recommended ~1600×500px",
    )
    link = models.CharField(
        "ბმული / Link", max_length=300, blank=True,
        help_text="Where the banner leads, e.g. /shop/knee-braces/",
    )
    sort_order = models.PositiveIntegerField("რიგითობა / Order", default=0)
    is_active = models.BooleanField("აქტიური / Active", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "ბანერი / Banner"
        verbose_name_plural = "ბანერები / Banners"

    def __str__(self):
        return self.title_ka or f"Banner #{self.pk}"


class BlogPost(TranslatableMixin, models.Model):
    title_ka = models.CharField("სათაური (ქართ.)", max_length=250)
    title_en = models.CharField("Title (EN)", max_length=250, blank=True)
    slug = models.SlugField(unique=True)
    cover = models.ImageField("ყდის სურათი / Cover", upload_to="blog/", blank=True)
    excerpt_ka = models.TextField("ანონსი (ქართ.)", blank=True, help_text="Short teaser for list pages")
    excerpt_en = models.TextField("Excerpt (EN)", blank=True)
    body_ka = models.TextField("ტექსტი (ქართ.)")
    body_en = models.TextField("Body (EN)", blank=True)
    is_published = models.BooleanField("გამოქვეყნებული / Published", default=True)
    published_at = models.DateTimeField("თარიღი / Date", default=timezone.now)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "სტატია / Blog post"
        verbose_name_plural = "ბლოგი / Blog posts"

    def __str__(self):
        return self.title_ka

    def get_absolute_url(self):
        return reverse("content:blog_detail", args=[self.slug])


class StoreLocation(TranslatableMixin, models.Model):
    name_ka = models.CharField("სახელი (ქართ.)", max_length=150)
    name_en = models.CharField("Name (EN)", max_length=150, blank=True)
    address_ka = models.CharField("მისამართი (ქართ.)", max_length=250)
    address_en = models.CharField("Address (EN)", max_length=250, blank=True)
    phone = models.CharField("ტელეფონი / Phone", max_length=30, blank=True)
    hours_ka = models.CharField("საათები (ქართ.)", max_length=120, default="ორშ–შაბ: 10:00 – 19:00")
    hours_en = models.CharField("Hours (EN)", max_length=120, default="Mon–Sat: 10:00 – 19:00")
    map_url = models.URLField("Google Maps ბმული", blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("აქტიური / Active", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "მაღაზია / Store location"
        verbose_name_plural = "მაღაზიები / Store locations"

    def __str__(self):
        return self.name_ka


class FAQ(TranslatableMixin, models.Model):
    question_ka = models.CharField("კითხვა (ქართ.)", max_length=300)
    question_en = models.CharField("Question (EN)", max_length=300, blank=True)
    answer_ka = models.TextField("პასუხი (ქართ.)")
    answer_en = models.TextField("Answer (EN)", blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("აქტიური / Active", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "კითხვა / FAQ"
        verbose_name_plural = "ხდკ / FAQ"

    def __str__(self):
        return self.question_ka


class SiteSettings(models.Model):
    """Singleton editable in admin: phone numbers & contact email shown across the site."""
    phone_primary = models.CharField("ძირითადი ნომერი / Primary phone", max_length=30)
    phone_secondary = models.CharField("მეორე ნომერი / Secondary phone", max_length=30)
    phone_trauma = models.CharField(
        "ტრავმატოლოგის ნომერი / Traumatologist on-call phone", max_length=30,
        help_text="Shown in the 'Traumatologist on call' block on the homepage",
    )
    phone_xray = models.CharField(
        "რენტგენის ნომერი / X-ray service phone", max_length=30,
        help_text="Shown in the 'X-ray at home' block on the homepage",
    )
    email = models.EmailField("ელფოსტა / Contact email")

    class Meta:
        verbose_name = "საიტის პარამეტრები / Site settings"
        verbose_name_plural = "საიტის პარამეტრები / Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        from django.conf import settings as dj
        obj, _ = cls.objects.get_or_create(pk=1, defaults={
            "phone_primary": dj.PHONE_PRIMARY,
            "phone_secondary": dj.PHONE_SECONDARY,
            "phone_trauma": dj.PHONE_TRAUMA,
            "phone_xray": dj.PHONE_XRAY,
            "email": dj.CONTACT_EMAIL,
        })
        return obj


class ContactMessage(models.Model):
    name = models.CharField("სახელი / Name", max_length=120)
    phone = models.CharField("ტელეფონი / Phone", max_length=30)
    message = models.TextField("შეტყობინება / Message", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField("დამუშავებული / Processed", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "შეტყობინება / Contact message"
        verbose_name_plural = "შეტყობინებები / Contact messages"

    def __str__(self):
        return f"{self.name} ({self.created_at:%d.%m.%Y})"
