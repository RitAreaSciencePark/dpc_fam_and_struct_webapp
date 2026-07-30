FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/RitAreaSciencePark/dpc_fam_and_struct_webapp"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY manage.py ./
COPY dpc_fam_and_struct_webapp/ ./dpc_fam_and_struct_webapp/
COPY dpc/ ./dpc/
COPY dpcfam/ ./dpcfam/
COPY dpcstruct/ ./dpcstruct/
COPY templates/ ./templates/
COPY static/images/ ./static/images/

RUN DJANGO_SECRET_KEY=build-only-not-for-runtime \
    DB_PASSWORD=build-only-not-for-runtime \
    DEBUG=False \
    python manage.py check \
    && DJANGO_SECRET_KEY=build-only-not-for-runtime \
    DB_PASSWORD=build-only-not-for-runtime \
    DEBUG=False \
    python manage.py collectstatic --noinput

RUN useradd \
    --create-home \
    --uid 10001 \
    --shell /usr/sbin/nologin \
    appuser

USER 10001:10001

EXPOSE 8000

HEALTHCHECK \
    --interval=30s \
    --timeout=3s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2).read()"

CMD ["gunicorn", "dpc_fam_and_struct_webapp.wsgi:application", "--bind=0.0.0.0:8000", "--workers=2", "--timeout=120", "--graceful-timeout=30", "--worker-tmp-dir=/tmp", "--access-logfile=-", "--error-logfile=-"]
