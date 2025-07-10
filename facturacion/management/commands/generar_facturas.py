from django.core.management.base import BaseCommand
from facturacion.models import Factura
from usuarios.models import Usuario
from datetime import date


class Command(BaseCommand):
    help = 'Genera facturas del mes actual para todos los usuarios'

    def handle(self, *args, **kwargs):
        hoy = date.today()
        periodo_inicio = date(hoy.year, hoy.month, 1)
        periodo_final = date(hoy.year, hoy.month, 30)

        for usuario in Usuario.objects.all():
            if Factura.objects.filter(usuario=usuario, periodo_inicio=periodo_inicio).exists():
                self.stdout.write(self.style.WARNING(
                    f"Ya existe factura para {usuario}"))
                continue

            factura = Factura.objects.create(
                usuario=usuario,
                codigo=hoy.month,
                periodo_inicio=periodo_inicio,
                periodo_final=periodo_final,
                monto_a_pagar=60000
            )

            self.stdout.write(self.style.SUCCESS(f"Factura creada para {usuario} - ID: {factura.factura_id}"))
