# G&T OrthoCare — Django E-Commerce

Monolithic Django 5.2 application for the G&T OrthoCare orthopedic equipment store.
Bilingual storefront (Georgian / English), a call-to-order product catalog (no online
prices or cart — customers phone in to order), and a fully branded admin panel
(django-unfold) where the product owner manages everything.

## Stack

Django 5.2 · SQLite (dev) / PostgreSQL (prod, via `DATABASE_URL`) · django-unfold admin ·
WhiteNoise static serving · Gunicorn · Pillow · Docker-ready.

## Project layout

```
django-app/
├── config/            settings, urls, wsgi, admin dashboard callback
├── apps/
│   ├── catalog/       Category, Product (+images), storefront views, seed command
│   ├── orders/        dormant Order models (kept for future use; not in customer flow)
│   └── content/       Banner, BlogPost, StoreLocation, FAQ, ContactMessage
├── templates/         storefront pages + admin dashboard override
├── static/            css/js/logo (design ported from the approved prototype)
├── Dockerfile         gunicorn + collectstatic + auto-migrate
└── requirements.txt
```

## Local development

```bash
cd django-app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo            # 7 categories, 33 products + photos, FAQs, store, 2 posts
python manage.py createsuperuser
python manage.py runserver
```

- Storefront: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

`seed_demo` copies product photos from `../website/assets` (the design prototype).
Use `--assets /path/to/folder` if you move things around. It is idempotent.

## What the product owner can edit in /admin

- **Products** — stock, sizes, photos (main + gallery), bilingual names and descriptions,
  featured flag (homepage "Popular products" block), bulk activate/feature/CSV export.
  (An optional internal price field exists but is never shown on the website.)
- **Site settings** — phone numbers (main, secondary, traumatologist on-call, X-ray) and
  contact email; edits apply instantly across the whole site.
- **Banners** — homepage hero carousel (upload ~1600×500 images; if none exist, the default
  branded hero is shown).
- **Blog, Store locations, FAQ, Contact messages (leads)** — full CRUD.
- **Dashboard** — new/today leads, active products, categories, featured count, low-stock
  alerts, 14-day messages chart, products-by-category, recent leads.

Give the PO a staff account: create a user in Admin → Users, set *staff status*, and assign
permissions (or superuser if they should see everything).

## Configuration (env vars)

Copy `.env.example` to `.env`. Key variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | required in production |
| `DEBUG` | `0` in production |
| `ALLOWED_HOSTS` | comma-separated, e.g. `gtorthocare.ge,www.gtorthocare.ge` |
| `CSRF_TRUSTED_ORIGINS` | `https://gtorthocare.ge,...` |
| `DATABASE_URL` | `postgres://user:pass@rds-host:5432/gtorthocare` (unset = SQLite) |
| `MEDIA_ROOT` | uploaded files location (mount a volume or switch to S3) |
| `EMAIL_*`, `ORDER_NOTIFICATION_EMAIL` | SMTP/SES for new-order emails (console backend by default) |

Business settings (delivery fee, free-delivery threshold, phones) live at the bottom of
`config/settings.py`.

## Deploying — Option A: single server (recommended, ~$12–15/mo)

Best price/simplicity at current traffic. One AWS Lightsail instance (or any VPS) runs the
whole stack via docker compose: **Postgres + Django + Caddy** (automatic HTTPS). Product
photos and the database live on the server disk in Docker volumes — no S3/RDS bills.

```bash
# 1. Lightsail: create Ubuntu instance (2 GB RAM bundle), attach static IP,
#    open ports 80+443 in its firewall. Point the domain's A record at the IP.
# 2. On the server:
sudo apt update && sudo apt install -y docker.io docker-compose-v2
git clone <your-repo> django-app && cd django-app     # or scp the folder
cp .env.example .env && nano .env                     # SECRET_KEY, DOMAIN=gtorthocare.ge,
                                                      # POSTGRES_PASSWORD, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS
docker compose up -d --build
docker compose exec app python manage.py seed_demo --assets ./seed-photos   # optional
docker compose exec app python manage.py createsuperuser

# 3. Nightly backups (DB + photos, 14-day retention):
crontab -e   # add:
# 0 3 * * * cd /home/ubuntu/django-app && ./scripts/backup.sh >> backups/backup.log 2>&1
```

Local dress rehearsal of the exact production stack:
`DOMAIN=":80" ALLOWED_HOSTS="*" docker compose up --build` → http://localhost

Updating the site later: `git pull && docker compose up -d --build` (photos and DB are in
volumes, untouched). If traffic ever grows: resize the Lightsail instance (minutes), or move
to Option B below — the same image runs there unchanged.

## Deploying — Option B: managed autoscaling (App Runner / ECS, ~$30–60/mo)

For when traffic justifies it. Containers here are ephemeral, so this option **requires
S3 for media** (django-storages, see settings.py comment).

1. **Database** — create an RDS PostgreSQL instance, set `DATABASE_URL`.
2. **Build & push** the image:
   ```bash
   docker build -t gt-orthocare .
   docker tag gt-orthocare:latest <acct>.dkr.ecr.<region>.amazonaws.com/gt-orthocare:latest
   docker push <acct>.dkr.ecr.<region>.amazonaws.com/gt-orthocare:latest
   ```
   The container runs `migrate` on start and serves via gunicorn on port 8000.
3. **Service** — App Runner / ECS service pointing at the image, env vars from the table above.
   Health check path: `/healthz`.
4. **Media files** — uploaded product photos must persist:
   - simplest: mount EFS at `MEDIA_ROOT`, or
   - best practice: S3 — `pip install django-storages[boto3]`, switch the `default` storage
     backend in `config/settings.py` (comment is already there), set the `AWS_*` vars.
5. **Static files** — served by WhiteNoise from the container; nothing extra needed.
6. **HTTPS** — terminate TLS at the ALB/CloudFront; `SECURE_PROXY_SSL_HEADER` is already
   configured for `X-Forwarded-Proto`.
7. **Email** — verify your domain in SES and set the `EMAIL_*` vars so new orders reach
   `ORDER_NOTIFICATION_EMAIL`.
8. **Seed production once**:
   ```bash
   python manage.py seed_demo --assets ./seed-photos   # or add products via admin
   python manage.py createsuperuser
   ```

Elastic Beanstalk (Docker platform) also works with zero changes: `eb init && eb create`,
set the same env vars.

## Notes / future work

- **Call-to-order model**: the storefront shows no prices and has no cart — every product
  page and card has a "Call to order" button (tel: link). Prices vary by partner/branch, so
  they're intentionally off the public site. The `orders` app (Order/OrderItem models) is kept
  dormant in the codebase should online ordering ever be wanted again.
- **Catalog quirk**: the printed catalog lists two different products as "A-06"; the black
  hand fixator was seeded as **A-07** — correct the code in admin if it has a real one.
- Tests: `python manage.py test apps` (20 tests: catalog, call-to-order, admin, leads).
