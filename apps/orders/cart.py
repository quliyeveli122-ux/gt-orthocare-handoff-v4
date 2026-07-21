"""Session cart. Stored as {"<product_id>:<size>": qty}."""
from decimal import Decimal

from django.conf import settings

from apps.catalog.models import Product

SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get(SESSION_KEY, {})

    def _save(self):
        self.session[SESSION_KEY] = self.data
        self.session.modified = True

    @staticmethod
    def key(product_id, size=""):
        return f"{product_id}:{size or ''}"

    def add(self, product, size="", qty=1):
        k = self.key(product.pk, size)
        self.data[k] = self.data.get(k, 0) + max(1, int(qty))
        self._save()

    def update(self, k, qty):
        if k in self.data:
            qty = int(qty)
            if qty <= 0:
                del self.data[k]
            else:
                self.data[k] = qty
            self._save()

    def remove(self, k):
        if k in self.data:
            del self.data[k]
            self._save()

    def clear(self):
        self.session[SESSION_KEY] = {}
        self.session.modified = True
        self.data = {}

    def count(self):
        return sum(self.data.values())

    def items(self):
        ids = {int(k.split(":")[0]) for k in self.data}
        products = {p.pk: p for p in Product.objects.filter(pk__in=ids, is_active=True)}
        out = []
        for k, qty in self.data.items():
            pid_str, _, size = k.partition(":")
            product = products.get(int(pid_str))
            if not product:
                continue
            out.append({
                "key": k,
                "product": product,
                "size": size,
                "qty": qty,
                "unit_price": product.current_price,
                "line_total": product.current_price * qty,
            })
        return out

    def items_total(self):
        return sum((i["line_total"] for i in self.items()), start=Decimal("0"))

    def delivery_fee(self):
        total = self.items_total()
        if total == 0 or total >= settings.FREE_DELIVERY_FROM:
            return Decimal("0")
        return Decimal(settings.DELIVERY_FEE)

    def grand_total(self):
        return self.items_total() + self.delivery_fee()
