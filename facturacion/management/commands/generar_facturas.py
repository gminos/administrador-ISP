from django.core.management.base import BaseCommand
from facturacion.models import Factura
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
        reconexion = date(hoy.year, hoy.month + 1, 5)

        for usuario in Usuario.objects.all():
            if Factura.objects.filter(usuario=usuario, periodo_inicio=periodo_inicio).exists():
                self.stdout.write(self.style.WARNING(
                    f"Ya existe factura para {usuario}"))
                continue

            instalaciones_activas = usuario.instalacion.filter(
                servicio_activo=True)
            monto = sum(
                inst.plan.costo for inst in instalaciones_activas
                if inst.plan and inst.plan.costo
            )

            factura = Factura.objects.create(
                usuario=usuario,
                codigo=hoy.month,
                periodo_inicio=periodo_inicio,
                periodo_final=periodo_final,
                fecha_reconexion=reconexion,
                monto_a_pagar=monto
            )

            self.stdout.write(self.style.SUCCESS(
                f"Factura creada para {usuario} - ID: {factura.factura_id}"
            ))
