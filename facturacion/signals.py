from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from instalaciones.models import Instalacion
from .models import Factura, DetallePago, Cargo

@receiver(post_save, sender=Instalacion)
def crear_cargo_por_instalacion(sender, instance, created, **kwargs):
    if created:
        Cargo.objects.create(
            cliente=instance.cliente,
            instalacion=instance,
            tipo_cargo="instalacion",
            fecha_emision=instance.fecha_instalacion,
            monto_total=instance.costo
        )

@receiver(post_save, sender=Factura)
def crear_cargo_por_factura(sender, instance, created, **kwargs):
    if created:
        costo = instance.instalacion.plan.costo if instance.instalacion.plan else 0
        Cargo.objects.create(
            cliente=instance.instalacion.cliente,
            instalacion=instance.instalacion,
            factura_origen=instance,
            fecha_vencimiento=instance.fecha_reconexion,
            monto_total=costo
        )

@receiver(post_delete, sender=DetallePago)
def restaurar_saldo_cargo_al_borrar_pago(sender, instance, **kwargs):
    cargo = instance.cargo
    cargo.saldo_pendiente += instance.monto_abonado

    if cargo.saldo_pendiente >= cargo.monto_total:
        cargo.estado = "pendiente"
    elif cargo.saldo_pendiente > 0:
        cargo.estado = "parcial"
    else:
        cargo.estado = "pagado"

    cargo.save(update_fields=["saldo_pendiente", "estado"])
