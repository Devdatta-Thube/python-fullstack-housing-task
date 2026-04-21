# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt ./
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=market_api.settings \
    DJANGO_DEBUG=0

COPY --from=builder /install /usr/local
COPY manage.py ./
COPY market_api ./market_api
COPY market ./market
COPY data ./data

# Collect static (DRF ships a browsable-API, but we disabled it; collectstatic
# is still useful because Django's staticfiles app is installed).
RUN mkdir -p staticfiles && python manage.py collectstatic --noinput

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health/', timeout=3).status in (200,503) else 1)"

CMD ["gunicorn", "market_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
