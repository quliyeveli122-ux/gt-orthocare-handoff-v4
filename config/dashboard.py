"""Admin dashboard KPIs — rendered by templates/admin/index.html via Unfold's DASHBOARD_CALLBACK.

Call-to-order catalog: no online orders/revenue, so the dashboard focuses on the
catalog health and incoming leads (contact messages)."""
import json
from datetime import timedelta

from django.conf import settings
from django.db.models import Count
from django.utils import timezone


def dashboard_callback(request, context):
    from apps.catalog.models import Category, Product
    from apps.content.models import ContactMessage

    now = timezone.localtime()
    today = now.date()

    low_stock = Product.objects.filter(is_active=True, stock__lte=settings.LOW_STOCK_THRESHOLD)

    # contact messages (leads) per day, last 14 days
    days, counts = [], []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        days.append(day.strftime("%d.%m"))
        counts.append(ContactMessage.objects.filter(created_at__date=day).count())

    top_categories = (
        Category.objects.filter(is_active=True)
        .annotate(n=Count("products", filter=None))
        .order_by("-n")[:5]
    )

    context.update({
        "kpi": {
            "products_total": Product.objects.filter(is_active=True).count(),
            "featured_total": Product.objects.filter(is_active=True, is_featured=True).count(),
            "categories_total": Category.objects.filter(is_active=True).count(),
            "low_stock_count": low_stock.count(),
            "messages_new": ContactMessage.objects.filter(is_processed=False).count(),
            "messages_today": ContactMessage.objects.filter(created_at__date=today).count(),
        },
        "recent_messages": ContactMessage.objects.order_by("-created_at")[:8],
        "low_stock_products": low_stock.order_by("stock")[:8],
        "top_categories": top_categories,
        "chart_labels": json.dumps(days),
        "chart_values": json.dumps(counts),
    })
    return context
