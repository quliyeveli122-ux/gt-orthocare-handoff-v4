from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action, display

from .models import FAQ, Banner, BlogPost, ContactMessage, SiteSettings, StoreLocation


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ["__str__", "phone_primary", "phone_trauma", "phone_xray", "email"]
    fieldsets = (
        ("ტელეფონები / Phone numbers", {
            "fields": ("phone_primary", "phone_secondary", "phone_trauma", "phone_xray"),
            "description": "ეს ნომრები ავტომატურად განახლდება საიტის ყველა გვერდზე — "
                           "ჰედერში, ღილაკებზე, სერვისების ბლოკებში და ფუტერში.",
        }),
        ("ელფოსტა / Email", {"fields": ("email",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ["thumb", "title_ka", "link", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]

    @display(description="")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:120px;height:38px;object-fit:cover;border-radius:6px">', obj.image.url)
        return "—"


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ["thumb", "title_ka", "published_at", "is_published"]
    list_editable = ["is_published"]
    list_filter = ["is_published"]
    search_fields = ["title_ka", "title_en"]
    prepopulated_fields = {"slug": ("title_en",)}
    date_hierarchy = "published_at"
    fieldsets = (
        (None, {"fields": ("title_ka", "title_en", "slug", "cover", ("is_published", "published_at"))}),
        ("ქართული / Georgian", {"fields": ("excerpt_ka", "body_ka")}),
        ("English", {"fields": ("excerpt_en", "body_en"), "classes": ("collapse",)}),
    )

    @display(description="")
    def thumb(self, obj):
        if obj.cover:
            return format_html('<img src="{}" style="width:64px;height:40px;object-fit:cover;border-radius:6px">', obj.cover.url)
        return "—"


@admin.register(StoreLocation)
class StoreLocationAdmin(ModelAdmin):
    list_display = ["name_ka", "address_ka", "phone", "hours_ka", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["name_ka", "address_ka"]


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ["question_ka", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["question_ka", "answer_ka"]


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ["name", "phone_link", "short_message", "created_at", "processed_badge"]
    list_filter = ["is_processed"]
    search_fields = ["name", "phone", "message"]
    readonly_fields = ["name", "phone", "message", "created_at"]
    actions = ["mark_processed"]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False  # messages come from the website form only

    @display(description="ტელეფონი / Phone")
    def phone_link(self, obj):
        return format_html('<a href="tel:{}" style="font-weight:600">{}</a>', obj.phone, obj.phone)

    @display(description="შეტყობინება / Message")
    def short_message(self, obj):
        return (obj.message[:80] + "…") if len(obj.message) > 80 else (obj.message or "—")

    @display(description="სტატუსი / Status", label={True: "success", False: "warning"})
    def processed_badge(self, obj):
        return obj.is_processed, "დამუშავებული" if obj.is_processed else "ახალი"

    @action(description="✓ დამუშავებულად მონიშვნა / Mark processed")
    def mark_processed(self, request, queryset):
        queryset.update(is_processed=True)
