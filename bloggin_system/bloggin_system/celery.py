from celery import Celery
import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloggin_system.settings')

app = Celery('bloggin_system')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
