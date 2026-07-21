import csv

from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["thumb", "name_ka", "name_en", "slug", "product_badge", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["name_ka", "name_en", "slug"]
    prepopulated_fields = {"slug": ("name_en",)}
    ordering = ["sort_order"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_n=Count("products"))

    @display(description="")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:8px">', obj.image.url)
        return "—"

    @display(description="პროდუქტები / Products", label=True)
    def product_badge(self, obj):
        return f"{obj._n}"


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0
    fields = ["image", "alt", "sort_order"]


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["thumb", "code", "name_ka", "category",
                    "stock_badge", "is_featured", "is_active"]
    list_editable = ["is_featured", "is_active"]
    list_filter = ["category", "is_active", "is_featured"]
    search_fields = ["code", "name_ka", "name_en", "slug"]
    prepopulated_fields = {"slug": ("code", "name_en")}
    inlines = [ProductImageInline]
    list_per_page = 25
    actions = ["make_active", "make_inactive", "make_featured", "unfeature", "export_csv"]
    readonly_fields = ["preview", "created_at", "updated_at"]
    fieldsets = (
        ("ძირითადი / Basics", {"fields": (("code", "category"), "slug", "name_ka", "name_en")}),
        ("მარაგი და ზომები / Stock & sizes", {"fields": (("stock", "sizes"),)}),
        ("აღწერა / Description", {"fields": ("description_ka", "description_en"), "classes": ("collapse",)}),
        ("სურათი / Image", {"fields": ("image", "preview")}),
        ("შიდა ფასი / Internal price", {
            "fields": ("price",), "classes": ("collapse",),
            "description": "არასავალდებულო — მხოლოდ შიდა მოხმარებისთვის. საიტზე ფასი არ ჩანს.",
        }),
        ("ხილვადობა / Visibility", {"fields": (("is_active", "is_featured"), ("created_at", "updated_at"))}),
    )

    # ---- list columns -------------------------------------------------
    @display(description="")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:44px;height:44px;object-fit:cover;border-radius:8px">', obj.image.url)
        return "—"

    @display(description="მარაგი / Stock", label={"danger": "danger", "warning": "warning", "success": "success"})
    def stock_badge(self, obj):
        from django.conf import settings
        if obj.stock == 0:
            return "danger", f"0 — ამოიწურა"
        if obj.stock <= settings.LOW_STOCK_THRESHOLD:
            return "warning", f"{obj.stock} — ცოტაა"
        return "success", str(obj.stock)

    @display(description="დიდი სურათი / Preview")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:280px;border-radius:12px">', obj.image.url)
        return "—"

    # ---- bulk actions --------------------------------------------------
    @action(description="✓ გააქტიურება / Activate")
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @action(description="✕ დამალვა / Deactivate")
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @action(description="★ მოთხოვნადებში / Feature")
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @action(description="☆ მოხსნა / Unfeature")
    def unfeature(self, request, queryset):
        queryset.update(is_featured=False)

    @action(description="⬇ CSV ექსპორტი / Export CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = "attachment; filename=products.csv"
        response.write("﻿")  # BOM so Excel opens Georgian text correctly
        writer = csv.writer(response)
        writer.writerow(["Code", "Name KA", "Name EN", "Category", "Price", "Sale price", "Stock", "Active"])
        for p in queryset.select_related("category"):
            writer.writerow([p.code, p.name_ka, p.name_en, p.category.name_ka,
                             p.price, p.sale_price or "", p.stock, p.is_active])
        return response
