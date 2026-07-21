from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import include, path


def set_language(request, lang):
    """Storefront KA/EN switch (session based)."""
    if lang in ("ka", "en"):
        request.session["lang"] = lang
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


def healthz(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("set-lang/<str:lang>/", set_language, name="set_language"),
    path("healthz", healthz, name="healthz"),
    path("", include("apps.content.urls")),
    path("", include("apps.catalog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
