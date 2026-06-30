from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import connection
from .models import Router

@receiver(post_save, sender=Router)
def sincronizar_planes_router_nuevo(sender, instance, created, **kwargs):
    if created:
        from redes.tasks import tarea_sincronizar_planes_router_nuevo
        schema_name = connection.schema_name
        if schema_name != 'public':
            tarea_sincronizar_planes_router_nuevo.delay(schema_name, instance.id)
