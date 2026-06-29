from redes.mikrotik_cliente import reactivar_cliente, suspender_clientes_masivo
from django_tenants.utils import schema_context
from instalaciones.models import Instalacion
from nucleo_admin.models import EmpresaISP
from celery import shared_task, Task
from collections import defaultdict
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def suspender_morosos_masivamente(self: Task) -> str:
    hoy = timezone.now().date()

    inquilinos = EmpresaISP.objects.exclude(schema_name='public')
    resultado_total = []

    for inquilino in inquilinos:
        with schema_context(inquilino.schema_name):
            morosos = Instalacion.objects.filter(
                servicio_activo=True,
                cargos__tipo_cargo='mensualidad',
                cargos__estado__in=['pendiente', 'parcial'],
                cargos__fecha_vencimiento__lt=hoy
            ).select_related('router', 'cliente').distinct()

            instalaciones_morosas = defaultdict(list)
            total_suspendidos_exitosos = []
            total_suspendidos_fallidos = []

            for instalacion in morosos:
                if not instalacion.router or not instalacion.pppoe_usuario:
                    logger.warning(f"Omitiendo {instalacion.cliente}: Sin router o usuario PPPoE configurado.")
                    continue

                router = instalacion.router
                instalaciones_morosas[router].append(instalacion.pppoe_usuario)

            for router, pppoe_usuarios in instalaciones_morosas.items():
                suspendidos_exitosos, suspendidos_fallidos = suspender_clientes_masivo(router, pppoe_usuarios)
                total_suspendidos_exitosos.extend(suspendidos_exitosos)
                total_suspendidos_fallidos.extend(suspendidos_fallidos)

            Instalacion.objects.filter(pppoe_usuario__in=total_suspendidos_exitosos).update(servicio_activo=False)

            if total_suspendidos_exitosos or total_suspendidos_fallidos:
                mensaje_resumen = f"[{inquilino.schema_name}] Suspendidos: {len(total_suspendidos_exitosos)}, Errores: {len(total_suspendidos_fallidos)}"
                logger.info(mensaje_resumen)

                if total_suspendidos_fallidos:
                    logger.error(f"[{inquilino.schema_name}] Fallaron estos usuarios PPPoE {','.join(total_suspendidos_fallidos)}")

                resultado_total.append(mensaje_resumen)

    if not resultado_total:
        return "No hubo morosos para suspender en ningún inquilino."

    return " | ".join(resultado_total)

@shared_task(bind=True)
def verificar_y_reactivar_instalacion(self: Task, instalacion_id: int, schema_name: str) -> str:
    with schema_context(schema_name):
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

@shared_task(bind=True, max_retries=3)
def tarea_sincronizar_perfil(self: Task, schema_name: str, plan_nombre: str, megas: int):
    from redes.models import Router
    from redes.mikrotik_cliente import sincronizar_perfil_ppp
    with schema_context(schema_name):
        routers = Router.objects.all()
        for router in routers:
            exito, msg = sincronizar_perfil_ppp(router, plan_nombre, megas)
            if not exito:
                logger.error(f"Error en tarea_sincronizar_perfil para router {router.ip}: {msg}")

@shared_task(bind=True, max_retries=3)
def tarea_eliminar_perfil(self: Task, schema_name: str, plan_nombre: str):
    from redes.models import Router
    from redes.mikrotik_cliente import eliminar_perfil_ppp
    with schema_context(schema_name):
        routers = Router.objects.all()
        for router in routers:
            exito, msg = eliminar_perfil_ppp(router, plan_nombre)
            if not exito:
                logger.error(f"Error en tarea_eliminar_perfil para router {router.ip}: {msg}")

@shared_task(bind=True, max_retries=3)
def tarea_sincronizar_secret(self: Task, schema_name: str, router_id: int, usuario: str, password: str, plan_nombre: str, ip_estatica: str = None):
    from redes.models import Router
    from redes.mikrotik_cliente import sincronizar_secret_ppp
    with schema_context(schema_name):
        try:
            router = Router.objects.get(pk=router_id)
            exito, msg = sincronizar_secret_ppp(router, usuario, password, plan_nombre, ip_estatica)
            if not exito:
                logger.error(f"Fallo sincronizando secret: {msg}")
                raise self.retry(countdown=10)
        except Router.DoesNotExist:
            logger.error(f"Router {router_id} no existe.")

@shared_task(bind=True, max_retries=3)
def tarea_eliminar_secret(self: Task, schema_name: str, router_id: int, usuario: str):
    from redes.models import Router
    from redes.mikrotik_cliente import eliminar_secret_ppp
    with schema_context(schema_name):
        try:
            router = Router.objects.get(pk=router_id)
            exito, msg = eliminar_secret_ppp(router, usuario)
            if not exito:
                logger.error(f"Fallo eliminando secret: {msg}")
                raise self.retry(countdown=10)
        except Router.DoesNotExist:
            logger.error(f"Router {router_id} no existe.")
