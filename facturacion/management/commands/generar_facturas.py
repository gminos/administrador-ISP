from django.db import transaction
from django.core.management.base import BaseCommand
from facturacion.models import Factura
from instalaciones.models import Instalacion
from datetime import date
import calendar


class Command(BaseCommand):
    help = 'Genera pagos del mes actual para todos los usuarios cuyo servicio se encuentre activo'

    @staticmethod
    def calculo_fechas(ciclo_facturacion: int) -> tuple[date, date, date]:
        fecha_hoy = date.today()
        year_siguiente = fecha_hoy.year if fecha_hoy.month < 12 else fecha_hoy.year + 1
        mes_siguiente = fecha_hoy.month + 1 if fecha_hoy.month < 12 else 1

        if ciclo_facturacion == 30:
            periodo_inicio = date(fecha_hoy.year, fecha_hoy.month, 1)
            ultimo_dia_del_mes = calendar.monthrange(fecha_hoy.year, fecha_hoy.month)[1]
            dia_final = 30 if ultimo_dia_del_mes >= 30 else ultimo_dia_del_mes
            periodo_final = date(fecha_hoy.year, fecha_hoy.month, dia_final)
            fecha_reconexion = date(year_siguiente, mes_siguiente, 3)

            return periodo_inicio, periodo_final, fecha_reconexion

        periodo_inicio = date(fecha_hoy.year, fecha_hoy.month, 15)
        periodo_final = date(year_siguiente, mes_siguiente, 14)
        fecha_reconexion = date(year_siguiente, mes_siguiente, 17)

        return periodo_inicio, periodo_final, fecha_reconexion

    def handle(self, *args, **kwargs):
        fecha_hoy = date.today()
        ultimo_dia_del_mes = calendar.monthrange(fecha_hoy.year, fecha_hoy.month)[1]
        ciclos_a_cobrar = [fecha_hoy.day]

        if fecha_hoy.day == ultimo_dia_del_mes and ultimo_dia_del_mes < 30:
            ciclos_a_cobrar.append(30)


        instalaciones_del_dia = Instalacion.objects.filter(ciclo_facturacion__in=ciclos_a_cobrar, servicio_activo=True)
        facturas_nuevas = []

        for instalacion in instalaciones_del_dia:
            periodo_inicio, periodo_final, fecha_reconexion = self.calculo_fechas(instalacion.ciclo_facturacion)

            if Factura.objects.filter(instalacion=instalacion, periodo_inicio=periodo_inicio).exists():
                self.stdout.write(self.style.WARNING(
                    f"Ya existe factura para {instalacion.cliente}"))
                continue

            factura_nueva = Factura(
                instalacion=instalacion,
                periodo_inicio=periodo_inicio,
                periodo_final=periodo_final,
                fecha_reconexion=fecha_reconexion,
            )

            facturas_nuevas.append(factura_nueva)

            self.stdout.write(self.style.SUCCESS(
                f"Factura genera para: {instalacion.cliente.nombre}"
            ))

        with transaction.atomic():
            for factura in facturas_nuevas:
                factura.save()
