from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import connection
from .models import Plan

@receiver(post_save, sender=Plan)
def sincronizar_plan_mikrotik(sender, instance, **kwargs):
    from redes.tasks import tarea_sincronizar_perfil
    schema_name = connection.schema_name
    if schema_name != 'public':
        tarea_sincronizar_perfil.delay(schema_name, instance.nombre, instance.cantidad_megas)

@receiver(post_delete, sender=Plan)
def eliminar_plan_mikrotik(sender, instance, **kwargs):
    from redes.tasks import tarea_eliminar_perfil
    schema_name = connection.schema_name
    if schema_name != 'public':
        tarea_eliminar_perfil.delay(schema_name, instance.nombre)
