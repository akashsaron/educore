import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

# Ensure Celery app is always imported when Django starts
from config.celery import app as celery_app  # noqa: F401, E402
