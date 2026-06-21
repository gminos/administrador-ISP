from facturacion.models import Factura, Transaccion, Cargo, DetallePago
from unfold.contrib.filters.admin import RadioFilter
from django.template.loader import render_to_string
from simple_history.admin import SimpleHistoryAdmin
from django.core.validators import EMPTY_VALUES
from facturacion.utils import generar_pdf_factura
from django.utils.formats import date_format
from unfold.decorators import display
from django.http import HttpResponse
from unfold.admin import ModelAdmin, TabularInline
from clientes.models import Cliente
from base.admin import admin_site
from django.contrib import admin
import weasyprint
import zipfile
import io


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
                return queryset.filter(cargo__estado="pagado")
            if self.value() == "pendiente":
                return queryset.filter(cargo__estado="pendiente")
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


@admin.register(Factura, site=admin_site)
class FacturaAdmin(ModelAdmin):
    list_select_related = [
        "instalacion",
        "instalacion__cliente"
    ]
    actions = ["descargar_pdf"]
    list_display = (
        "cliente",
        "cliente_vereda",
        "estado_pago",
        "periodo_facturado",
        "fecha_reconexion_formateada",
    )
    search_fields = (
        "instalacion__cliente__nombre",
        "instalacion__cliente__apellido"
    )
    autocomplete_fields = ["instalacion"]
    date_hierarchy = "periodo_inicio"
    ordering = (
        "periodo_inicio",
        "instalacion__cliente__vereda",
        "instalacion__cliente__nombre",
    )
    list_per_page = 100
    list_filter = [EstadoPagoFilter, VeredaFilter,]
    list_filter_submit = True
    show_facets = admin.ShowFacets.NEVER
    readonly_fields = ["estado"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("instalacion__cliente", "cargo")

    @admin.action(description="Descargar Factura(s) en PDF")
    def descargar_pdf(self, request, queryset):
        if queryset.count() == 1:
            factura = queryset.first()
            pdf = generar_pdf_factura(factura)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="factura_{factura.pk}.pdf"'
            return response
        else:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for factura in queryset:
                    pdf = generar_pdf_factura(factura)
                    zip_file.writestr(f'factura_{factura.pk}.pdf', pdf)

            response = HttpResponse(buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="facturas.zip"'
            return response

    @admin.display(description="cliente")
    def cliente(self, obj):
        return f'{obj.cliente.nombre} {obj.cliente.apellido}'

    @display(
        description="Estado del pago",
        label={
            "pagado": "success",
            "parcial": "warning",
            "pendiente": "danger"
        }
    )
    def estado_pago(self, obj):
        return obj.estado

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


class DetallePagoInline(TabularInline):
    model = DetallePago
    extra = 0
    readonly_fields = ["transaccion", "cargo", "saldo_previo", "monto_abonado", "saldo_restante"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Transaccion, site=admin_site)
class TransaccionAdmin(ModelAdmin, SimpleHistoryAdmin):
    actions = ["descargar_pdf"]
    list_display = [
        "referencia_formateada",
        "cliente",
        "monto_total",
        "metodo_pago",
        "fecha_pago",
    ]

    @display(description="N° Transacción")
    def referencia_formateada(self, obj):
        return f"#{obj.id:05d}"
    list_filter = [
        "metodo_pago",
        "fecha_pago"
    ]
    search_fields = [
        "cliente__nombre",
        "cliente__apellido",
        "id"
    ]
    date_hierarchy = "fecha_pago"
    readonly_fields = [
        "cliente",
        "monto_total",
        "metodo_pago",
        "fecha_pago"
    ]
    inlines = [DetallePagoInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("cliente")

    @admin.action(description="Descargar Comprobante(s) en PDF")
    def descargar_pdf(self, request, queryset):
        if queryset.count() == 1:
            transaccion = queryset.first()
            html_string = render_to_string('facturacion/recibo_transaccion_pdf.html', {'transaccion': transaccion})
            html = weasyprint.HTML(string=html_string)
            pdf = html.write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="comprobante_{transaccion.pk}.pdf"'
            return response
        else:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for transaccion in queryset:
                    html_string = render_to_string('facturacion/recibo_transaccion_pdf.html', {'transaccion': transaccion})
                    html = weasyprint.HTML(string=html_string)
                    pdf = html.write_pdf()
                    zip_file.writestr(f"comprobante_{transaccion.pk}.pdf", pdf)

            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="comprobantes.zip"'
            return response

@admin.register(Cargo, site=admin_site)
class CargoAdmin(ModelAdmin, SimpleHistoryAdmin):
    list_display = (
        "referencia_formateada",
        "cliente",
        "tipo_cargo",
        "monto_total",
        "saldo_pendiente",
        "estado_cargo",
        "fecha_emision",
        "fecha_vencimiento"
    )

    @display(description="N° Ref.")
    def referencia_formateada(self, obj):
        return f"#{obj.id:05d}"
    list_filter = [
        "estado",
        "tipo_cargo"
    ]
    search_fields = [
        "cliente__nombre",
        "cliente__apellido",
        "id"
    ]
    date_hierarchy = "fecha_emision"
    autocomplete_fields = [
        "cliente",
        "instalacion",
        "factura_origen"
    ]
    readonly_fields = ["saldo_pendiente"]
    inlines = [DetallePagoInline]

    @display(
        description="Estado",
        label={
            "pagado": "success",
            "parcial": "warning",
            "pendiente": "danger"
        }
    )
    def estado_cargo(self, obj):
        return obj.estado
