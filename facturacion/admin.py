from django.contrib import admin
from .models import Factura, Pago
from base.admin import admin_site
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter

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
    list_display = ("cliente", "usuario_vereda", "codigo_factura", "periodo_facturado",
                    "fecha_reconexion_formateada", "monto_formateado", "estado_pago", "fecha_pago")
    search_fields = ("usuario__nombre", "usuario__apellido")
    autocomplete_fields = ["usuario"]
    inlines = [PagoInline]
    list_filter = (MesFiltro,)
    ordering = ("codigo_factura", "usuario__vereda", "usuario__nombre",)

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


admin_site.register(Factura, FacturaAdmin)
