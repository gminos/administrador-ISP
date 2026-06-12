
from django.db import migrations
from django.utils import timezone

def transferir_pagos_a_transacciones(apps, schema_editor):
    Pago = apps.get_model('facturacion', 'Pago')
    Transaccion = apps.get_model('facturacion', 'Transaccion')
    for pago in Pago.objects.all():
        fecha_segura = pago.fecha_pago if pago.fecha_pago else timezone.now().date()
        nueva_transaccion = Transaccion.objects.create(
            cliente=pago.factura.instalacion.cliente,
            fecha_pago=fecha_segura,
            monto_total=pago.monto_pagado,
        )
        pago.transaccion = nueva_transaccion
        pago.save()

class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0013_transaccion_pago_transaccion'),
    ]

    operations = [
        migrations.RunPython(transferir_pagos_a_transacciones),
    ]
