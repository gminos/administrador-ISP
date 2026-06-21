from facturacion.services.whatsapp import enviar_factura_cliente, enviar_comprobante_pago
from facturacion.models import Factura, Transaccion
from celery import shared_task, Task
from django.core.management import call_command
from django.utils import timezone

@shared_task(bind=True)
def procesar_envio_facturas(self: Task) -> str:
    hoy = timezone.now().date()

    facturas_a_enviar = Factura.objects.filter(
        periodo_inicio__year=hoy.year,
        periodo_inicio__month=hoy.month,
        estado__in=["pendiente", "parcial"],
        notificacion_enviada=False
    ).select_related('instalacion__cliente').prefetch_related('pagos')

    facturas_exitosas = []
    total_errores = 0

    for factura in facturas_a_enviar:
        exito = enviar_factura_cliente(factura)

        if exito:
            facturas_exitosas.append(factura.pk)
        else:
            total_errores += 1

    if facturas_exitosas:
        Factura.objects.filter(pk__in=facturas_exitosas).update(notificacion_enviada=True)

    resultado = f"Proceso masivo completado. Enviadas: {len(facturas_exitosas)}, Errores: {total_errores}"
    print(resultado)
    return resultado

@shared_task(bind=True, max_retries=5)
def procesar_envio_comprobando_whatsapp(self: Task, transaccion_id) -> None:
    try:
        transaccion = Transaccion.objects.get(pk=transaccion_id)
        exito = enviar_comprobante_pago(transaccion)
        if not exito:
            retraso = 60 * (2 ** self.request.retries)
            print(f"Reintentando envio de recibo {transaccion_id} en {retraso} segundos...")
            raise self.retry(countdown=retraso)
    except Transaccion.DoesNotExist:
        pass

@shared_task
def procesar_generacion_masiva_facturas() -> str:
    call_command('generar_facturas')
    return "Comando generar_facturas ejecutado con éxito."
