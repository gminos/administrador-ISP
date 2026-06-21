from redes.mikrotik_cliente import suspender_cliente
from redes.mikrotik_cliente import reactivar_cliente
from instalaciones.models import Instalacion
from celery import shared_task, Task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def suspender_morosos_masivamente(self: Task) -> str:
    hoy = timezone.now().date()

    morosos = Instalacion.objects.filter(
        servicio_activo=True,
        cargos__tipo_cargo='mensualidad',
        cargos__estado__in=['pendiente', 'parcial'],
        cargos__fecha_vencimiento__lt=hoy
    ).select_related('router', 'cliente').distinct()

    suspendidos_exitosos = []
    total_errores = 0

    for instalacion in morosos:
        if not instalacion.router or not instalacion.pppoe_usuario:
            logger.warning(f"Omitiendo {instalacion.cliente}: Sin router o usuario PPPoE configurado.")
            continue

        exito, mensaje = suspender_cliente(instalacion.router, instalacion.pppoe_usuario)

        if exito:
            instalacion.servicio_activo = False
            instalacion.save(update_fields=['servicio_activo'])
            suspendidos_exitosos.append(instalacion.pppoe_usuario)
            logger.info(f"Suspendido exitosamente: {instalacion.pppoe_usuario}")
        else:
            total_errores += 1
            logger.error(f"Fallo al suspender a {instalacion.pppoe_usuario}: {mensaje}")

    resultado = f"Corte automático nocturno completado. Suspendidos: {len(suspendidos_exitosos)}, Errores: {total_errores}"
    print(resultado)
    return resultado

@shared_task(bind=True)
def verificar_y_reactivar_instalacion(self: Task, instalacion_id: int) -> str:
    hoy = timezone.now().date()
    try:
        instalacion = Instalacion.objects.get(pk=instalacion_id, servicio_activo=False)

        tiene_vencidos = instalacion.cargos.filter(
            tipo_cargo='mensualidad',
            estado__in=['pendiente', 'parcial'],
            fecha_vencimiento__lt=hoy
        ).exists()

        if not tiene_vencidos:
            if not instalacion.router or not instalacion.pppoe_usuario:
                return f"Omitido: {instalacion.cliente} no tiene router o usuario PPPoE."

            exito, msg = reactivar_cliente(instalacion.router, instalacion.pppoe_usuario)
            if exito:
                instalacion.servicio_activo = True
                instalacion.save(update_fields=['servicio_activo'])
                logger.info(f"Reactivado exitosamente (pago registrado): {instalacion.pppoe_usuario}")
                return f"Reactivado exitosamente: {instalacion.pppoe_usuario}"
            else:
                logger.error(f"Fallo al reactivar a {instalacion.pppoe_usuario}: {msg}")
                return f"Error en Mikrotik: {msg}"
        else:
            return f"El cliente {instalacion.cliente} aún tiene facturas vencidas."

    except Instalacion.DoesNotExist:
        return f"Instalación {instalacion_id} no encontrada o ya esta activa."
