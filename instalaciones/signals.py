from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import connection
from .models import Instalacion
from redes.tasks import tarea_eliminar_secret, tarea_sincronizar_secret

@receiver(pre_save, sender=Instalacion)
def chequear_cambio_usuario_mikrotik(sender, instance, **kwargs):
    if not instance.pk:
        return

    schema_name = connection.schema_name
    if schema_name != 'public':
        try:
            instalacion_antigua = Instalacion.objects.get(pk=instance.pk)
            if instalacion_antigua.pppoe_usuario and instalacion_antigua.pppoe_usuario != instance.pppoe_usuario:
                if instalacion_antigua.router:
                    tarea_eliminar_secret.delay(
                        schema_name,
                        instalacion_antigua.router.id,
                        instalacion_antigua.pppoe_usuario
                    )
        except Instalacion.DoesNotExist:
            pass

@receiver(post_save, sender=Instalacion)
def sincronizar_instalacion_mikrotik(sender, instance, **kwargs):
    schema_name = connection.schema_name
    if schema_name != 'public':
        if instance.router and instance.pppoe_usuario and instance.plan:
            tarea_sincronizar_secret.delay(
                schema_name, 
                instance.router.id, 
                instance.pppoe_usuario, 
                instance.pppoe_password, 
                instance.plan.nombre,
                str(instance.ip_estatica) if instance.ip_estatica else None
            )

@receiver(post_delete, sender=Instalacion)
def eliminar_instalacion_mikrotik(sender, instance, **kwargs):
    schema_name = connection.schema_name
    if schema_name != 'public':
        if instance.router and instance.pppoe_usuario:
            tarea_eliminar_secret.delay(
                schema_name, 
                instance.router.id, 
                instance.pppoe_usuario
            )
