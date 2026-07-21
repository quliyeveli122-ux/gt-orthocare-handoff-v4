FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Migrations run on start so the container works with a fresh database.
# --forwarded-allow-ips="*" lets gunicorn trust X-Forwarded-Proto from the
# reverse proxy (Caddy/ALB); safe because port 8000 is never exposed publicly.
CMD python manage.py migrate --noinput && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} --timeout 60 --forwarded-allow-ips="*"
