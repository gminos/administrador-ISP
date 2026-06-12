from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from facturacion.models import Factura, Pago
from clientes.models import Cliente
from base.admin import admin_site
from django.utils.html import format_html
from django.utils.formats import date_format
from django.db import models
from unfold.widgets import UnfoldAdminDateWidget
from unfold.contrib.filters.admin import RadioFilter
from django.core.validators import EMPTY_VALUES
from django.http import HttpResponse
from django.template.loader import render_to_string
from unfold.decorators import action
import weasyprint
import zipfile
import io


class PagoInline(TabularInline):
    model = Pago
    verbose_name_plural = "Gestiona pagos"
    extra = 0


class EstadoPagoFilter(RadioFilter):
    title = "estado del pago"
    parameter_name = "estado_pago"
    all_option = None

    def lookups(self, request, model_admin):
        return (
            ("pagado", "Pagado"),
            ("pendiente", "Pendiente"),
        )

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            if self.value() == "pagado":
                return queryset.filter(estado="pagado")
            if self.value() == "pendiente":
                return queryset.filter(estado="pendiente")
        return queryset


class VeredaFilter(RadioFilter):
    title = "ubicacion"
    parameter_name = "instalacion__cliente__vereda"

    def lookups(self, request, model_admin):
        veredas = Cliente.objects.values_list('vereda', flat=True).distinct().order_by('vereda')
        return [(v, v) for v in veredas if v]

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            if self.value():
                return queryset.filter(instalacion__cliente__vereda=self.value())
        return queryset


@admin.register(Factura)
class FacturaAdmin(ModelAdmin):
    formfield_overrides = {
        models.DateField: {"widget": UnfoldAdminDateWidget},
    }
    list_select_related = ["instalacion","instalacion__cliente"]
    actions = ["descargar_pdf"]
    list_display = (
        "cliente",
        "cliente_vereda",
        "estado_pago",
        "fecha_pago",
        "total_pagado",
        "periodo_facturado",
        "fecha_reconexion_formateada",
    )
    search_fields = ("instalacion__cliente__nombre", "instalacion__cliente__apellido")
    autocomplete_fields = ["instalacion"]
    inlines = [PagoInline]
    date_hierarchy = "periodo_final"
    ordering = ("periodo_inicio__month","instalacion__cliente__vereda", "instalacion__cliente__nombre",)
    list_per_page = 100
    list_filter = [EstadoPagoFilter, VeredaFilter,]
    list_filter_submit = True
    show_facets = admin.ShowFacets.NEVER
    readonly_fields = ["estado"]


    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("pagos__transaccion")

    @action(description="Descargar Factura(s) en PDF")
    def descargar_pdf(self, request, queryset):
        if queryset.count() == 1:
            factura = queryset.first()
            saldos_anteriores = sum([f.saldo_pendiente for f in Factura.objects.filter(instalacion=factura.instalacion, estado__in=['pendiente', 'parcial'], periodo_inicio__lt=factura.periodo_inicio)])
            total_a_pagar = factura.saldo_pendiente + saldos_anteriores

            html_string = render_to_string('facturacion/factura_pdf.html', {
                'factura': factura, 
                'saldos_anteriores': saldos_anteriores, 
                'total_a_pagar': total_a_pagar
            })
            html = weasyprint.HTML(string=html_string)
            pdf = html.write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="factura_{factura.pk}.pdf"'
            return response
        else:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for factura in queryset:
                    saldos_anteriores = sum([f.saldo_pendiente for f in Factura.objects.filter(instalacion=factura.instalacion, estado__in=['pendiente', 'parcial'], periodo_inicio__lt=factura.periodo_inicio)])
                    total_a_pagar = factura.saldo_pendiente + saldos_anteriores
                    html_string = render_to_string('facturacion/factura_pdf.html', {
                        'factura': factura, 
                        'saldos_anteriores': saldos_anteriores, 
                        'total_a_pagar': total_a_pagar
                    })
                    html = weasyprint.HTML(string=html_string)
                    pdf = html.write_pdf()
                    zip_file.writestr(f'factura_{factura.pk}.pdf', pdf)

            response = HttpResponse(buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="facturas.zip"'
            return response

    @admin.display(description="cliente")
    def cliente(self, obj):
        return f'{obj.cliente.nombre} {obj.cliente.apellido}'

    @admin.display(description="estado del pago")
    def estado_pago(self, obj):
        if obj.estado == "pagado":
            color = "green"
        elif obj.estado == "parcial":
            color = "orange"
        else:
            color = "red"

        estado = obj.estado.capitalize()
        return format_html('<span style="color:{};">{}</span>', color, estado)

    @admin.display(description="total pagado")
    def total_pagado(self, obj):
        total = sum(p.monto_pagado for p in obj.pagos.all())

        return "{:,.2f}".format(total).replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="fecha de pago")
    def fecha_pago(self, obj):
        pagos = [pago for pago in obj.pagos.all() if pago.transaccion and pago.transaccion.fecha_pago]

        if pagos:
            fecha = max(p.transaccion.fecha_pago for p in pagos)
            dia = fecha.day
            mes = date_format(fecha, "F")
            year = fecha.year
            return f"{dia} de {mes} - {year}"

        return "Sin pago registrado"

    @admin.display(description="vereda")
    def cliente_vereda(self, obj):
        return obj.cliente.vereda

    @admin.display(description="periodo facturado")
    def periodo_facturado(self, obj):
        if not obj.periodo_final:
            return "-"

        dia_inicio = obj.periodo_inicio.day
        mes_inicio = date_format(obj.periodo_inicio, "F").capitalize()
        dia_final = obj.periodo_final.day
        mes_final = date_format(obj.periodo_final, "F").capitalize()

        return f"{dia_inicio} {mes_inicio} ~ {dia_final} {mes_final}"

    @admin.display(description="fecha reconexion")
    def fecha_reconexion_formateada(self, obj):
        if not obj.fecha_reconexion:
            return "-"
        dia_reconexion = obj.fecha_reconexion.day
        mes_reconexion = date_format(obj.fecha_reconexion, "F").capitalize()

        return f"{dia_reconexion} {mes_reconexion}"


@admin.register(Pago)
class PagoAdmin(ModelAdmin):
    list_display = (
        "cliente",
        "factura",
        "monto_pagado",
        "tipo_pago",
        "metodo_pago",
        "fecha_pago",
    )
    list_filter = ["tipo_pago", "transaccion__metodo_pago"]
    search_fields = ["factura__instalacion__cliente__nombre", "factura__instalacion__cliente__apellido"]
    list_select_related = ["factura", "factura__instalacion__cliente", "transaccion"]
    autocomplete_fields = ["factura"]

    @admin.display(description="cliente")
    def cliente(self, obj):
        if obj.factura and obj.factura.cliente:
            return f'{obj.factura.cliente.nombre} {obj.factura.cliente.apellido}'
        return "-"

    @admin.display(description="metodo de pago", ordering="transaccion__metodo_pago")
    def metodo_pago(self, obj):
        return obj.transaccion.metodo_pago.capitalize() if obj.transaccion and obj.transaccion.metodo_pago else "-"

    @admin.display(description="fecha de pago", ordering="transaccion__fecha_pago")
    def fecha_pago(self, obj):
        return obj.transaccion.fecha_pago if obj.transaccion else "-"

admin_site.register(Factura, FacturaAdmin)
admin_site.register(Pago, PagoAdmin)
