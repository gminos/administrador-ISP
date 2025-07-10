from django.core.management.base import BaseCommand
from facturacion.models import Factura, Pago
from usuarios.models import Usuario
from datetime import date
import calendar

YEAR_INICIO = 2025
MES_INICIO = 7


class Command(BaseCommand):
    help = 'Genera facturas del mes actual para todos los usuarios'

    def handle(self, *args, **kwargs):
        hoy = date.today()

        periodo_inicio = date(hoy.year, hoy.month, 1)
        ultimo_dia_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]
        dia_final = 30 if ultimo_dia_del_mes >= 30 else ultimo_dia_del_mes
        periodo_final = date(hoy.year, hoy.month, dia_final)

        mes_reconexion = hoy.month + 1 if hoy.month < 12 else 1
        año_reconexion = hoy.year if hoy.month < 12 else hoy.year + 1
        fecha_reconexion = date(año_reconexion, mes_reconexion, 5)

        numero_periodo = (hoy.year - YEAR_INICIO) * 12 + \
            (hoy.month - MES_INICIO) + 1
        codigo_generado = f"ART-{numero_periodo:03d}"

        for usuario in Usuario.objects.all():
            if Factura.objects.filter(usuario=usuario, periodo_inicio=periodo_inicio).exists():
                self.stdout.write(self.style.WARNING(
                    f"Ya existe factura para {usuario}"))
                continue

            instalaciones_activas = usuario.instalacion.filter(
                servicio_activo=True)
            monto_actual = sum(
                inst.plan.costo for inst in instalaciones_activas
                if inst.plan and inst.plan.costo
            )

            facturas_pendientes = Factura.objects.filter(
                usuario=usuario
            ).exclude(periodo_inicio=periodo_inicio)

            deuda_anterior = 0
            for factura in facturas_pendientes:
                pagos_pendientes = factura.pagos.filter(
                    estado="se acumula")
                deuda_anterior += sum(pago.monto_pagado for pago in pagos_pendientes)

            monto_total = monto_actual + deuda_anterior

            factura = Factura.objects.create(
                usuario=usuario,
                codigo_factura=codigo_generado,
                periodo_inicio=periodo_inicio,
                periodo_final=periodo_final,
                fecha_reconexion=fecha_reconexion,
                monto_a_pagar=monto_total,
            )

            Pago.objects.create(
                factura=factura,
                monto_pagado=monto_total,
                metodo_pago="no aplica",
                estado="pendiente"
            )

            self.stdout.write(self.style.SUCCESS(
                f"Factura creada para {usuario} - ID: {factura.factura_id}"
            ))
