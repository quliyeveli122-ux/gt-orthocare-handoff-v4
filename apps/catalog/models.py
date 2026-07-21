from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class TranslatableMixin:
    """Bilingual field helper: obj.t('name', 'en') -> name_en, falling back to Georgian."""

    def t(self, field, lang="ka"):
        return getattr(self, f"{field}_{lang}", "") or getattr(self, f"{field}_ka", "")


class Category(TranslatableMixin, models.Model):
    name_ka = models.CharField("სახელი (ქართ.)", max_length=120)
    name_en = models.CharField("Name (EN)", max_length=120, blank=True)
    slug = models.SlugField(unique=True, help_text="URL part, e.g. knee-braces")
    image = models.ImageField("სურათი / Image", upload_to="categories/", blank=True)
    sort_order = models.PositiveIntegerField("რიგითობა / Order", default=0)
    is_active = models.BooleanField("აქტიური / Active", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "კატეგორია / Category"
        verbose_name_plural = "კატეგორიები / Categories"

    def __str__(self):
        return self.name_ka

    def get_absolute_url(self):
        return reverse("catalog:shop_category", args=[self.slug])


class Product(TranslatableMixin, models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products",
        verbose_name="კატეგორია / Category",
    )
    code = models.CharField(
        "ორთოპედიული კოდი / Code", max_length=20, unique=True,
        help_text="Catalog code doctors put on prescriptions, e.g. M-02",
    )
    slug = models.SlugField(unique=True)
    name_ka = models.CharField("სახელი (ქართ.)", max_length=200)
    name_en = models.CharField("Name (EN)", max_length=200, blank=True)
    description_ka = models.TextField("აღწერა (ქართ.)", blank=True)
    description_en = models.TextField("Description (EN)", blank=True)
    # Prices are not shown on the storefront (call-to-order catalog). Kept optional
    # for internal reference only; vary by partner/branch so left blank by default.
    price = models.DecimalField(
        "შიდა ფასი / Internal price (₾)", max_digits=8, decimal_places=2,
        null=True, blank=True, help_text="Internal reference only — never shown on the website",
    )
    sale_price = models.DecimalField(
        "ფასდაკლებული ფასი / Sale price (₾)", max_digits=8, decimal_places=2,
        null=True, blank=True, help_text="Unused — discounts are disabled",
    )
    stock = models.PositiveIntegerField("მარაგი / Stock", default=10)
    sizes = models.CharField(
        "ზომები / Sizes", max_length=60, default="S,M,L,XL", blank=True,
        help_text="Comma separated (S,M,L,XL). Empty = universal size",
    )
    image = models.ImageField("მთავარი სურათი / Main image", upload_to="products/")
    is_active = models.BooleanField("აქტიური / Active", default=True)
    is_featured = models.BooleanField(
        "მოთხოვნადი / Featured", default=False,
        help_text="Shown in the 'Popular products' block on the homepage",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "პროდუქტი / Product"
        verbose_name_plural = "პროდუქტები / Products"
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["code"])]

    def __str__(self):
        return f"{self.code} — {self.name_ka}"

    def clean(self):
        if self.sale_price is not None and self.price is not None and self.sale_price >= self.price:
            raise ValidationError({"sale_price": "Sale price must be lower than the regular price."})

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    # -- pricing helpers -------------------------------------------------
    @property
    def has_sale(self):
        return self.sale_price is not None

    @property
    def current_price(self):
        return self.sale_price if self.has_sale else self.price

    @property
    def discount_percent(self):
        if not self.has_sale:
            return 0
        return round((1 - self.sale_price / self.price) * 100)

    @property
    def size_list(self):
        return [s.strip() for s in self.sizes.split(",") if s.strip()]

    @property
    def in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("სურათი / Image", upload_to="products/gallery/")
    alt = models.CharField("ალტ ტექსტი / Alt text", max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "დამატებითი სურათი / Extra image"
        verbose_name_plural = "დამატებითი სურათები / Extra images"

    def __str__(self):
        return f"{self.product.code} image #{self.pk}"
