from django.core.management.base import BaseCommand
from facturacion.models import Factura, Pago
from usuarios.models import Usuario
from datetime import date
import calendar


class Command(BaseCommand):
    help = 'Genera facturas del mes actual para todos los usuarios'

    def handle(self, *args, **kwargs):
        hoy = date.today()

        periodo_inicio = date(hoy.year, hoy.month, 1)
        ultimo_dia_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]
        dia_final = 30 if ultimo_dia_del_mes >= 30 else ultimo_dia_del_mes
        periodo_final = date(hoy.year, hoy.month, dia_final)

        mes_reconexion = hoy.month + 1 if hoy.month < 12 else 1
        year_reconexion = hoy.year if hoy.month < 12 else hoy.year + 1
        fecha_reconexion = date(year_reconexion, mes_reconexion, 5)

        for usuario in Usuario.objects.all():
            if Factura.objects.filter(usuario=usuario, periodo_inicio=periodo_inicio).exists():
                self.stdout.write(self.style.WARNING(
                    f"Ya existe factura para {usuario}"))
                continue

            instalaciones_activas = usuario.instalacion.filter(
                servicio_activo=True)
            monto_a_pagar = sum(
                inst.plan.costo for inst in instalaciones_activas
                if inst.plan and inst.plan.costo
            )

            factura = Factura.objects.create(
                usuario=usuario,
                periodo_inicio=periodo_inicio,
                periodo_final=periodo_final,
                fecha_reconexion=fecha_reconexion,
                monto_a_pagar=monto_a_pagar,
            )

            Pago.objects.create(
                factura=factura,
                monto_pagado=monto_a_pagar,
                metodo_pago="no aplica",
                estado="pendiente"
            )

            self.stdout.write(self.style.SUCCESS(
                f"Factura creada para {usuario} - ID: {factura.factura_id}"
            ))
