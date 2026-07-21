import random

from django.db import models
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "ახალი / New"
        CONFIRMED = "confirmed", "დადასტურებული / Confirmed"
        SHIPPED = "shipped", "გზაშია / Shipped"
        DELIVERED = "delivered", "მიწოდებული / Delivered"
        CANCELLED = "cancelled", "გაუქმებული / Cancelled"

    class Payment(models.TextChoices):
        COD = "cod", "კურიერთან გადახდა / Cash on delivery"
        CARD = "card", "ბარათით (ონლაინ) / Card online"  # ready for a future gateway

    number = models.CharField("ნომერი / Number", max_length=20, unique=True, blank=True)
    status = models.CharField("სტატუსი / Status", max_length=12, choices=Status.choices, default=Status.NEW)
    payment_method = models.CharField("გადახდა / Payment", max_length=8, choices=Payment.choices, default=Payment.COD)

    customer_name = models.CharField("მომხმარებელი / Customer", max_length=120)
    phone = models.CharField("ტელეფონი / Phone", max_length=30)
    city = models.CharField("ქალაქი / City", max_length=80, default="თბილისი")
    address = models.CharField("მისამართი / Address", max_length=250)
    comment = models.TextField("კომენტარი / Comment", blank=True)

    items_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    admin_note = models.TextField("შიდა შენიშვნა / Internal note", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "შეკვეთა / Order"
        verbose_name_plural = "შეკვეთები / Orders"

    def __str__(self):
        return f"{self.number} — {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    def _generate_number(self):
        prefix = timezone.localtime().strftime("GT-%y%m%d")
        for _ in range(20):
            candidate = f"{prefix}-{random.randint(1000, 9999)}"
            if not Order.objects.filter(number=candidate).exists():
                return candidate
        return f"{prefix}-{random.randint(10000, 99999)}"

    def recalc(self, save=True):
        self.items_total = sum((i.line_total for i in self.items.all()), start=0)
        self.grand_total = self.items_total + self.delivery_fee
        if save:
            self.save(update_fields=["items_total", "grand_total"])

    @property
    def item_count(self):
        return sum(i.quantity for i in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="order_items", verbose_name="პროდუქტი / Product",
    )
    # snapshot fields — stay correct even if the product is edited/deleted later
    code = models.CharField("კოდი / Code", max_length=20)
    name = models.CharField("სახელი / Name", max_length=200)
    size = models.CharField("ზომა / Size", max_length=20, blank=True)
    unit_price = models.DecimalField("ერთ. ფასი / Unit price", max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField("რაოდ. / Qty", default=1)
    line_total = models.DecimalField("ჯამი / Line total", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "შეკვეთის პროდუქტი / Order item"
        verbose_name_plural = "შეკვეთის პროდუქტები / Order items"

    def __str__(self):
        return f"{self.code} ×{self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
