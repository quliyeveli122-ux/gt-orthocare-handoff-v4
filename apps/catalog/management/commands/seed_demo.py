"""
Seed the database with the G&T OrthoCare catalog (7 categories, 33 products),
store location, FAQs and two sample blog posts.

Product photos are copied from the design prototype's assets folder:
    manage.py seed_demo --assets ../website/assets
Idempotent: running twice updates instead of duplicating.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import Category, Product
from apps.content.models import FAQ, BlogPost, StoreLocation

CATEGORIES = [
    # slug, name_ka, name_en, image product code
    ("wrist-hand", "მაჯისა და ხელის ფიქსატორები", "Wrist & Hand Braces", "A-05"),
    ("ankle-foot", "კოჭისა და ტერფის ფიქსატორები", "Ankle & Foot Braces", "XF-01"),
    ("knee", "მუხლის ფიქსატორები", "Knee Braces", "M-02"),
    ("shoulder-arm", "მხრისა და მკლავის ფიქსატორები", "Shoulder & Arm Supports", "T-01"),
    ("finger-toe", "თითის ფიქსატორები", "Finger & Toe Splints", "P-01"),
    ("compression", "კომპრესია და დამჭერები", "Compression & Supports", "OW-01"),
    ("mobility", "გადაადგილების საშუალებები", "Mobility Aids", "MF-03"),
]

DESCRIPTIONS = {
    "wrist-hand": (
        "უზრუნველყოფს მაჯისა და ხელის საიმედო ფიქსაციას ტრავმის, ოპერაციის შემდგომ პერიოდში ან პროფილაქტიკისთვის. რეგულირებადი სამაგრები ზუსტი მორგებისთვის.",
        "Provides reliable wrist and hand fixation after injury, surgery, or for prevention. Adjustable straps for a precise fit.",
    ),
    "ankle-foot": (
        "უზრუნველყოფს კოჭ-ტერფის სტაბილიზაციას და იცავს განმეორებითი ტრავმისგან მკურნალობისა და რეაბილიტაციის პერიოდში.",
        "Stabilizes the ankle and foot and protects against re-injury during treatment and rehabilitation.",
    ),
    "knee": (
        "უზრუნველყოფს მუხლის სახსრის ფიქსაციას და მხარდაჭერას — ტრავმის, ოპერაციის შემდგომ ან სპორტული დატვირთვისას.",
        "Provides knee joint fixation and support — after injury, surgery, or during sports activity.",
    ),
    "shoulder-arm": (
        "უზრუნველყოფს მხრისა და მკლავის იმობილიზაციას, ამცირებს ტკივილს და აჩქარებს გამოჯანმრთელებას.",
        "Immobilizes the shoulder and arm, reduces pain and speeds up recovery.",
    ),
    "finger-toe": (
        "აფიქსირებს თითს სწორ პოზიციაში მოტეხილობის ან დაზიანების დროს. მსუბუქი და კომფორტული ტარებისას.",
        "Fixes the finger in the correct position after a fracture or injury. Light and comfortable to wear.",
    ),
    "compression": (
        "აუმჯობესებს სისხლის მიმოქცევას და ამცირებს შეშუპებას. იდეალურია ყოველდღიური ტარებისთვის და სპორტისთვის.",
        "Improves blood circulation and reduces swelling. Ideal for daily wear and sports.",
    ),
    "mobility": (
        "საიმედო დამხმარე საშუალება უსაფრთხო გადაადგილებისთვის რეაბილიტაციის პერიოდში.",
        "A reliable aid for safe movement during the rehabilitation period.",
    ),
}

SIZES_DEFAULT = "S,M,L,XL"
PRODUCTS = [
    # code, cat_slug, name_ka, name_en, price, featured, sizes
    ("A-01", "wrist-hand", "მაჯა-ხელის მყარი ორთეზი", "Rigid Wrist-Hand Orthosis", 85, False, SIZES_DEFAULT),
    ("A-02", "wrist-hand", "მაჯის ორთეზი თასმებით", "Wrist Lacing Orthosis with Splints", 95, False, SIZES_DEFAULT),
    ("A-03", "wrist-hand", "მაჯის ფიქსატორი შინით", "Wrist Splint Brace", 55, False, SIZES_DEFAULT),
    ("A-04", "wrist-hand", "თითების დამჭიმი ორთეზი", "Finger Extension Splint", 40, False, SIZES_DEFAULT),
    ("A-05", "wrist-hand", "ცერა თითის ფიქსატორი", "Thumb Spica Splint", 45, True, SIZES_DEFAULT),
    ("A-06", "wrist-hand", "ხელის მოსასვენებელი ორთეზი", "Resting Hand Splint", 110, False, SIZES_DEFAULT),
    ("A-07", "wrist-hand", "ხელისგულის ფიქსატორი", "Metacarpal Hand Fixator", 60, False, SIZES_DEFAULT),
    ("P-01", "finger-toe", "თითის ალუმინის შინა", "Aluminum Finger Splint", 18, False, ""),
    ("P-02", "finger-toe", "ფეხის თითის ფიქსატორი", "Toe Splint", 22, False, ""),
    ("T-01", "shoulder-arm", "მხრის იმობილაიზერი", "Shoulder Immobilizer", 75, True, SIZES_DEFAULT),
    ("T-02", "shoulder-arm", "მკლავის დამჭერი (ბადისებრი)", "Mesh Arm Sling", 45, False, SIZES_DEFAULT),
    ("T-03", "shoulder-arm", "მკლავის დამჭერი", "Arm Sling", 38, False, SIZES_DEFAULT),
    ("K-01", "ankle-foot", "კოჭის მყარი ორთეზი", "Rigid Ankle Orthosis", 120, False, SIZES_DEFAULT),
    ("K-02", "ankle-foot", "კოჭ-ტერფის ორთეზი", "Ankle-Foot Orthosis", 130, False, SIZES_DEFAULT),
    ("K-03", "ankle-foot", "ორთოპედიული ჩექმა (Walker)", "Walker Boot", 220, True, SIZES_DEFAULT),
    ("K-05", "ankle-foot", "კოჭის ელასტიკური დამჭერი", "Elastic Ankle Support", 35, False, SIZES_DEFAULT),
    ("K-07", "ankle-foot", "კოჭ-ტერფის მყარი ჩექმა", "Rigid AFO Boot", 160, False, SIZES_DEFAULT),
    ("K-08", "ankle-foot", "კოჭ-ტერფის ფიქსატორი", "Ankle-Foot Splint", 95, False, SIZES_DEFAULT),
    ("K-09", "ankle-foot", "კოჭის სტაბილიზატორი თასმებით", "Ankle Stabilizer with Straps", 65, False, SIZES_DEFAULT),
    ("XF-01", "ankle-foot", "სპორტული კოჭის ორთეზი", "Sport Ankle Brace", 140, True, SIZES_DEFAULT),
    ("KN-04", "ankle-foot", "ვალგუსის კორექტორი", "Bunion Corrector", 30, False, ""),
    ("M-01", "knee", "მუხლის იმობილაიზერი", "Knee Immobilizer", 110, False, SIZES_DEFAULT),
    ("M-02", "knee", "მუხლის სახსრიანი ორთეზი", "Hinged Knee Brace", 150, True, SIZES_DEFAULT),
    ("M-03", "knee", "მუხლის ნაქსოვი დამჭერი", "Knitted Knee Support", 85, False, SIZES_DEFAULT),
    ("M-04", "knee", "მუხლის ზამბარიანი ორთეზი", "Knee Power-Assist Brace", 90, False, SIZES_DEFAULT),
    ("M-05", "knee", "პოსტოპერაციული მუხლის ორთეზი (ROM)", "Post-Op ROM Knee Brace", 260, True, "უნივერსალური"),
    ("M-07", "knee", "სპორტული მუხლის დამჭერი", "Sports Knee Support", 55, False, SIZES_DEFAULT),
    ("M-08", "knee", "მუხლის ფიქსატორი პატელას ღიობით", "Knee Brace with Patella Opening", 95, False, SIZES_DEFAULT),
    ("OW-01", "compression", "საკომპრესიო წინდები", "Compression Socks", 45, True, "S,M,L"),
    ("FT-03", "compression", "იდაყვის ნაქსოვი დამჭერი", "Knitted Elbow Support", 70, False, SIZES_DEFAULT),
    ("MF-01", "mobility", "იდაყვის ყავარჯნები (წყვილი)", "Forearm Crutches (Pair)", 95, False, ""),
    ("MF-02", "mobility", "იღლიის ყავარჯნები (წყვილი)", "Underarm Crutches (Pair)", 70, False, ""),
    ("MF-03", "mobility", "დასაკეცი ვოკერი", "Folding Walker", 150, True, ""),
]

FAQS = [
    ("როგორ შევუკვეთო პროდუქტი ექიმის დანიშნულებით?",
     "How do I order with a doctor's prescription?",
     "დანიშნულების ფურცელზე მითითებულია პროდუქტის ორთოპედიული კოდი (მაგ. M-02). მოძებნეთ კოდი საიტზე ან დაგვირეკეთ და ოპერატორი გაგიფორმებთ შეკვეთას.",
     "Your prescription sheet contains the product's orthopedic code (e.g. M-02). Search for the code on our website, or call us and our operator will place the order for you."),
    ("რამდენ ხანში მოხდება მიწოდება?",
     "How fast is delivery?",
     "საკურიერო მომსახურება მუშაობს მთელი საქართველოს მასშტაბით — მიწოდება ხდება 24 საათში.",
     "Our courier service covers all of Georgia — delivery within 24 hours."),
    ("როგორ შევარჩიო სწორი ზომა?",
     "How do I choose the right size?",
     "თითოეულ პროდუქტს აქვს ზომების არჩევანი (S/M/L/XL). თუ არ ხართ დარწმუნებული, დაგვირეკეთ — კონსულტანტი დაგეხმარებათ ზომის შერჩევაში.",
     "Each product has size options (S/M/L/XL). If unsure, call us — a consultant will help you choose."),
    ("როგორ ხდება გადახდა?",
     "How do I pay?",
     "გადახდა ხდება კურიერთან — ნაღდი ანგარიშსწორებით ან ბარათით მიწოდებისას.",
     "Payment is made to the courier — cash or card on delivery."),
]

BLOG_POSTS = [
    ("rogor-avirchiot-muxlis-fiqsatori", "M-02",
     "როგორ ავირჩიოთ მუხლის ფიქსატორი?", "How to choose a knee brace?",
     "მუხლის ფიქსატორის სწორად შერჩევა დამოკიდებულია ტრავმის ტიპსა და მკურნალობის ეტაპზე.",
     "Choosing the right knee brace depends on the type of injury and the stage of treatment.",
     "მუხლის ფიქსატორის შერჩევისას გასათვალისწინებელია რამდენიმე ფაქტორი: ტრავმის ტიპი, მკურნალობის ეტაპი და ექიმის რეკომენდაცია.\n\nიმობილაიზერი გამოიყენება მწვავე ტრავმის ან ოპერაციის შემდგომ პერიოდში, როცა საჭიროა სახსრის სრული ფიქსაცია. სახსრიანი ორთეზი საშუალებას იძლევა კონტროლირებადი მოძრაობისთვის რეაბილიტაციის ეტაპზე. ნაქსოვი დამჭერი კი იდეალურია ყოველდღიური და სპორტული დატვირთვისთვის.\n\nზუსტი მოდელის შესარჩევად მიმართეთ ექიმს — დანიშნულების ფურცელზე მითითებული კოდით კი პროდუქტს მარტივად იპოვით ჩვენს საიტზე.",
     "When choosing a knee brace, several factors matter: the type of injury, the stage of treatment, and your doctor's recommendation.\n\nAn immobilizer is used after acute trauma or surgery when the joint needs full fixation. A hinged orthosis allows controlled movement during rehabilitation. A knitted support is ideal for daily wear and sports.\n\nAsk your doctor for the exact model — with the code from your prescription sheet you can easily find the product on our website."),
    ("sakompresio-windebi-vis-schirdeba", "OW-01",
     "საკომპრესიო წინდები — ვის სჭირდება?", "Compression socks — who needs them?",
     "საკომპრესიო ნაწარმი აუმჯობესებს სისხლის მიმოქცევას და ამცირებს ფეხების დაღლილობას.",
     "Compression wear improves blood circulation and reduces leg fatigue.",
     "საკომპრესიო წინდები რეკომენდებულია ვარიკოზის პროფილაქტიკისთვის, ორსულობის პერიოდში, ხანგრძლივი ფრენების დროს და მათთვის, ვინც დღის დიდ ნაწილს ფეხზე დგომაში ატარებს.\n\nკომპრესიის ხარისხი განსხვავებულია — პროფილაქტიკურიდან სამკურნალომდე. სწორი კლასის შესარჩევად გაიარეთ კონსულტაცია ექიმთან ან დაგვირეკეთ.",
     "Compression socks are recommended for varicose vein prevention, during pregnancy, on long flights, and for anyone who spends much of the day standing.\n\nCompression levels vary — from preventive to medical grade. Consult your doctor to choose the right class, or simply give us a call."),
]


class Command(BaseCommand):
    help = "Seed categories, products (with photos), store, FAQs and sample blog posts"

    def add_arguments(self, parser):
        default_assets = settings.BASE_DIR / "seed-photos"          # self-contained copy
        if not default_assets.exists():                              # fallback: design prototype
            default_assets = settings.BASE_DIR.parent / "website" / "assets"
        parser.add_argument("--assets", default=str(default_assets),
                            help="Folder with <CODE>.jpg product photos")

    def handle(self, *args, **opts):
        assets = Path(opts["assets"])
        if not assets.exists():
            self.stdout.write(self.style.WARNING(f"Assets folder not found: {assets} — seeding without images"))

        cats = {}
        for i, (slug, ka, en, img_code) in enumerate(CATEGORIES):
            cat, _ = Category.objects.update_or_create(
                slug=slug, defaults={"name_ka": ka, "name_en": en, "sort_order": i, "is_active": True},
            )
            cats[slug] = (cat, img_code)

        created = updated = 0
        for code, cat_slug, ka, en, price, featured, sizes in PRODUCTS:
            cat, _img = cats[cat_slug]
            desc_ka, desc_en = DESCRIPTIONS[cat_slug]
            product, was_created = Product.objects.update_or_create(
                code=code,
                defaults={
                    "category": cat,
                    "slug": slugify(f"{code}-{en}") or slugify(code),
                    "name_ka": ka, "name_en": en,
                    "description_ka": desc_ka, "description_en": desc_en,
                    "price": price, "sale_price": None,
                    "stock": 10, "sizes": sizes,
                    "is_active": True, "is_featured": featured,
                },
            )
            img_path = assets / f"{code}.jpg"
            if img_path.exists() and not product.image:
                with open(img_path, "rb") as fh:
                    product.image.save(f"{code}.jpg", File(fh), save=True)
            created += was_created
            updated += not was_created

        # category images = representative product photo
        for slug, (cat, img_code) in cats.items():
            img_path = assets / f"{img_code}.jpg"
            if img_path.exists() and not cat.image:
                with open(img_path, "rb") as fh:
                    cat.image.save(f"cat-{slug}.jpg", File(fh), save=True)

        StoreLocation.objects.update_or_create(
            name_ka="G&T OrthoCare — სათაო ოფისი",
            defaults={
                "name_en": "G&T OrthoCare — Head Office",
                "address_ka": "თბილისი, საქართველო",
                "address_en": "Tbilisi, Georgia",
                "phone": "+995 514 06 88 06",
                "sort_order": 0, "is_active": True,
            },
        )

        for i, (q_ka, q_en, a_ka, a_en) in enumerate(FAQS):
            FAQ.objects.update_or_create(
                question_ka=q_ka,
                defaults={"question_en": q_en, "answer_ka": a_ka, "answer_en": a_en,
                          "sort_order": i, "is_active": True},
            )

        for slug, cover_code, t_ka, t_en, e_ka, e_en, b_ka, b_en in BLOG_POSTS:
            post, _ = BlogPost.objects.update_or_create(
                slug=slug,
                defaults={"title_ka": t_ka, "title_en": t_en, "excerpt_ka": e_ka, "excerpt_en": e_en,
                          "body_ka": b_ka, "body_en": b_en, "is_published": True},
            )
            cover = assets / f"{cover_code}.jpg"
            if cover.exists() and not post.cover:
                with open(cover, "rb") as fh:
                    post.cover.save(f"post-{slug}.jpg", File(fh), save=True)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {len(CATEGORIES)} categories, {created} products created / {updated} updated, "
            f"{len(FAQS)} FAQs, {len(BLOG_POSTS)} blog posts, 1 store."
        ))
