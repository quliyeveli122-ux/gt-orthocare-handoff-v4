from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalog.i18n import UI

from .forms import ContactForm
from .models import FAQ, BlogPost, StoreLocation


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    page = Paginator(posts, 9).get_page(request.GET.get("page"))
    return render(request, "storefront/blog_list.html", {"page": page})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    others = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3]
    return render(request, "storefront/blog_detail.html", {"post": post, "others": others})


def stores(request):
    return render(request, "storefront/stores.html", {
        "stores": StoreLocation.objects.filter(is_active=True),
    })


def faq(request):
    return render(request, "storefront/faq.html", {
        "faqs": FAQ.objects.filter(is_active=True),
    })


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            lang = request.session.get("lang", "ka")
            messages.success(request, UI[lang]["formOk"])
            return redirect(request.POST.get("next") or "content:contact")
    return render(request, "storefront/contact.html", {"form": form})
