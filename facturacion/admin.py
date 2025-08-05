from pathlib import Path
from django.contrib import admin
from .models import Factura, Pago
from base.admin import admin_site
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.urls import path
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.conf import settings

MESES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


class PagoInline(admin.TabularInline):
    model = Pago
    verbose_name_plural = "Gestiona pagos"
    extra = 0


class MesFiltro(SimpleListFilter):
    title = 'Mes de facturación'
    parameter_name = 'mes'

    def lookups(self, request, model_admin):
        return [(str(i), MESES[i].capitalize()) for i in range(1, 13)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(periodo_inicio__month=self.value())
        return queryset


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        "cliente",
        "usuario_vereda",
        "estado_pago",
        "fecha_pago",
        "monto_formateado",
        "descargar_pdf",
        "codigo_factura",
        "periodo_facturado",
        "fecha_reconexion_formateada",
    )
    search_fields = ("usuario__nombre", "usuario__apellido")
    autocomplete_fields = ["usuario"]
    inlines = [PagoInline]
    list_filter = (MesFiltro,)
    ordering = ("usuario__vereda", "usuario__nombre",)

    def cliente(self, obj):
        return f'{obj.usuario.nombre} {obj.usuario.apellido}'
    cliente.short_description = "cliente"

    def estado_pago(self, obj):
        pago = obj.pagos.filter(tipo_pago="mensualidad").first()
        if pago:
            color = "green" if pago.estado == "pagado" else "red"
            estado = pago.estado.capitalize()
        else:
            color = "red"
            estado = "Pendiente"
        return format_html('<span style="color:{};">{}</span>', color, estado)

    estado_pago.short_description = "Estado del pago"

    def monto_formateado(self, obj):
        return f"{obj.monto_a_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    monto_formateado.short_description = 'valor a pagar'
    monto_formateado.admin_order_field = 'monto_a_pagar'

    def fecha_pago(self, obj):
        pago = obj.pagos.filter(tipo_pago="mensualidad",
                                estado="pagado").first()
        if pago:
            fecha = pago.fecha_pago
            dia = fecha.day
            mes = MESES[fecha.month]
            year = fecha.year
            return f"{dia} de {mes} - {year}"
        return "Sin pago registrado"

    fecha_pago.short_description = "fecha de pago"

    def usuario_vereda(self, obj):
        return obj.usuario.vereda

    usuario_vereda.short_description = "vereda"

    def periodo_facturado(self, obj):
        dia_inicio = obj.periodo_inicio.day
        dia_final = obj.periodo_final.day
        mes = MESES[obj.periodo_final.month].capitalize()
        return f"{dia_inicio} ~ {dia_final} {mes}"

    periodo_facturado.short_description = "periodo facturado"

    def fecha_reconexion_formateada(self, obj):
        dia_reconexion = obj.fecha_reconexion.day
        mes_reconexion = MESES[obj.fecha_reconexion.month].capitalize()
        return f"{dia_reconexion} {mes_reconexion}"

    fecha_reconexion_formateada.short_description = "fecha reconexion"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:factura_id>/pdf/',
                self.admin_site.admin_view(self.generar_pdf),
                name='factura-pdf',
            ),
        ]
        return custom_urls + urls

    def generar_pdf(self, request, factura_id):
        factura = Factura.objects.get(pk=factura_id)

        html_string = render_to_string('facturas/factura_pdf.html', {
            'factura': factura,
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename=factura_{
            factura.usuario.nombre}_{factura.usuario.apellido}.pdf'

        base_url = (Path(settings.STATIC_ROOT)).as_uri()

        HTML(string=html_string, base_url=base_url).write_pdf(response)

        return response

    def descargar_pdf(self, obj):
        return format_html(
            '<a class="link" href="{}">Descargar PDF</a>',
            f'{obj.factura_id}/pdf/'
        )

    descargar_pdf.short_description = 'PDF'
    descargar_pdf.allow_tags = True


admin_site.register(Factura, FacturaAdmin)
