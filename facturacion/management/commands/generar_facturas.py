from django.core.management.base import BaseCommand
from facturacion.models import Factura, Pago
from clientes.models import Cliente
from datetime import date
import calendar


class Command(BaseCommand):
    help = 'Genera pagos del mes actual para todos los usuarios cuyo servicio se encuentre activo'

    def handle(self, *args, **kwargs):
        hoy = date.today()

        periodo_inicio = date(hoy.year, hoy.month, 1)
        ultimo_dia_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]
        dia_final = 30 if ultimo_dia_del_mes >= 30 else ultimo_dia_del_mes
        periodo_final = date(hoy.year, hoy.month, dia_final)

        mes_reconexion = hoy.month + 1 if hoy.month < 12 else 1
        year_reconexion = hoy.year if hoy.month < 12 else hoy.year + 1
        fecha_reconexion = date(year_reconexion, mes_reconexion, 5)

        for cliente in Cliente.objects.all():
            if Factura.objects.filter(cliente=cliente, periodo_inicio=periodo_inicio).exists():
                self.stdout.write(self.style.WARNING(
                    f"Ya existe factura para {cliente}"))
                continue

            instalaciones_activas = cliente.instalacion.filter(
                servicio_activo=True)

            if not instalaciones_activas.exists():
                self.stdout.write(self.style.WARNING(
                    f"No hay servicios activos para {cliente}"))
                continue

            monto_a_pagar = sum(
                inst.plan.costo for inst in instalaciones_activas
                if inst.plan and inst.plan.costo
            )

            factura = Factura.objects.create(
                cliente=cliente,
                periodo_inicio=periodo_inicio,
                periodo_final=periodo_final,
                fecha_reconexion=fecha_reconexion,
            )

            Pago.objects.create(
                factura=factura,
                monto_pagado=monto_a_pagar,
                metodo_pago="no aplica",
                estado="pendiente"
            )

            self.stdout.write(self.style.SUCCESS(
                f"Pago generado para {cliente}"
            ))
