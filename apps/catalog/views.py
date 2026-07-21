from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from apps.content.forms import ContactForm
from apps.content.models import Banner, BlogPost

from .models import Category, Product

PAGE_SIZE = 12


def home(request):
    categories = Category.objects.filter(is_active=True).annotate(
        n=Count("products", filter=Q(products__is_active=True))
    )
    featured = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:8]
    return render(request, "storefront/home.html", {
        "banners": Banner.objects.filter(is_active=True),
        "categories": categories,
        "featured": featured,
        "hero_products": featured[:4],
        "posts": BlogPost.objects.filter(is_published=True)[:3],
        "contact_form": ContactForm(),
    })


def shop(request, cat_slug=None):
    products = Product.objects.filter(is_active=True).select_related("category")
    category = None
    if cat_slug:
        category = get_object_or_404(Category, slug=cat_slug, is_active=True)
        products = products.filter(category=category)

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(code__icontains=q) | Q(name_ka__icontains=q) | Q(name_en__icontains=q)
        )

    sort = request.GET.get("sort", "def")
    if sort == "asc":
        products = products.order_by("price")
    elif sort == "desc":
        products = products.order_by("-price")
    elif sort == "new":
        products = products.order_by("-created_at")

    paginator = Paginator(products, PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.filter(is_active=True).annotate(
        n=Count("products", filter=Q(products__is_active=True))
    )
    return render(request, "storefront/shop.html", {
        "page": page, "category": category, "categories": categories,
        "q": q, "sort": sort, "total": paginator.count,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug, is_active=True,
    )
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]
    sizes = product.size_list
    default_size = sizes[1] if len(sizes) > 1 else (sizes[0] if sizes else "")
    return render(request, "storefront/product_detail.html", {
        "product": product, "related": related, "default_size": default_size,
    })
