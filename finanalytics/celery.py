import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanalytics.settings')
app = Celery('finanalytics')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-db-every-midnight':{
        'task': 'mainview.tasks.update_db',
        'schedule' : crontab(minute=0, hour=0)
    }
}