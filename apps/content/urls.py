from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("stores/", views.stores, name="stores"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
]
