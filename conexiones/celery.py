from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conexiones.settings')

app = Celery('conexiones')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'generar-facturas-mensuales-diario': {
        'task': 'facturacion.tasks.procesar_generacion_masiva_facturas',
        'schedule': crontab(hour=1, minute=0),
    },
    'enviar-facturas-whatsapp-diario': {
        'task': 'facturacion.tasks.procesar_envio_facturas',
        'schedule': crontab(hour=8, minute=0),
    },
}
