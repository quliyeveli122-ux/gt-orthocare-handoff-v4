from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.i18n import UI
from apps.catalog.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


def cart_detail(request):
    cart = Cart(request)
    return render(request, "storefront/cart.html", {"cart": cart})


@require_POST
def cart_add(request):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=request.POST.get("product_id"), is_active=True)
    size = request.POST.get("size", "").strip()[:20]
    qty = request.POST.get("qty", 1)
    try:
        qty = max(1, min(99, int(qty)))
    except (TypeError, ValueError):
        qty = 1
    cart.add(product, size=size, qty=qty)

    if request.headers.get("x-requested-with") == "fetch":
        lang = request.session.get("lang", "ka")
        return JsonResponse({"count": cart.count(), "message": f"{product.t('name', lang)} — {UI[lang]['added']}"})
    return redirect("orders:cart_detail")


@require_POST
def cart_update(request):
    cart = Cart(request)
    cart.update(request.POST.get("key", ""), request.POST.get("qty", 1))
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request):
    cart = Cart(request)
    cart.remove(request.POST.get("key", ""))
    return redirect("orders:cart_detail")


def checkout(request):
    cart = Cart(request)
    if cart.count() == 0:
        return redirect("orders:cart_detail")

    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        order = Order.objects.create(
            payment_method=Order.Payment.COD,
            delivery_fee=cart.delivery_fee(),
            **form.cleaned_data,
        )
        for item in cart.items():
            product = item["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                code=product.code,
                name=product.name_ka,
                size=item["size"],
                unit_price=item["unit_price"],
                quantity=item["qty"],
            )
            # decrement stock, never below zero
            product.stock = max(0, product.stock - item["qty"])
            product.save(update_fields=["stock"])
        order.recalc()
        _notify(order)
        cart.clear()
        request.session["last_order"] = order.number
        return redirect("orders:success")

    return render(request, "storefront/checkout.html", {"cart": cart, "form": form})


def success(request):
    number = request.session.get("last_order")
    if not number:
        return redirect("catalog:home")
    order = Order.objects.filter(number=number).first()
    return render(request, "storefront/order_success.html", {"order": order})


def _notify(order):
    """Email the shop about a new order. Console backend in dev; SMTP via env in prod."""
    recipient = settings.ORDER_NOTIFICATION_EMAIL
    if not recipient:
        return
    lines = [f"{i.code} | {i.name} | {i.size or '-'} | {i.quantity} x {i.unit_price} = {i.line_total} GEL"
             for i in order.items.all()]
    body = (
        f"New order {order.number}\n\n"
        f"Customer: {order.customer_name}\nPhone: {order.phone}\n"
        f"City: {order.city}\nAddress: {order.address}\nComment: {order.comment or '-'}\n\n"
        + "\n".join(lines)
        + f"\n\nDelivery: {order.delivery_fee} GEL\nTOTAL: {order.grand_total} GEL"
    )
    send_mail(
        subject=f"[G&T OrthoCare] New order {order.number}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=True,
    )
