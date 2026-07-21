from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("add/", views.cart_add, name="cart_add"),
    path("update/", views.cart_update, name="cart_update"),
    path("remove/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/", views.success, name="success"),
]
