from django.conf import settings


def storefront(request):
    from .i18n import UI
    from .models import Category

    lang = request.session.get("lang", "ka")
    if lang not in ("ka", "en"):
        lang = "ka"

    # contact details are editable in admin (SiteSettings); fall back to settings.py
    try:
        from apps.content.models import SiteSettings
        s = SiteSettings.load()
        contact = {"phone1": s.phone_primary, "phone2": s.phone_secondary,
                   "phone_trauma": s.phone_trauma, "phone_xray": s.phone_xray, "email": s.email}
    except Exception:
        contact = {"phone1": settings.PHONE_PRIMARY, "phone2": settings.PHONE_SECONDARY,
                   "phone_trauma": settings.PHONE_TRAUMA, "phone_xray": settings.PHONE_XRAY,
                   "email": settings.CONTACT_EMAIL}

    return {
        "LANG": lang,
        "T": UI[lang],
        "NAV_CATEGORIES": Category.objects.filter(is_active=True),
        "SITE": {
            "name": settings.SITE_NAME,
            "free_delivery_from": settings.FREE_DELIVERY_FROM,
            **contact,
        },
    }
