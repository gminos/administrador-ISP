from django.contrib import admin
from .models import Factura, Pago, DetalleFactura
from base.admin import admin_site
from django.utils.html import format_html


class PagoInline(admin.TabularInline):
    model = Pago
    verbose_name_plural = "Gestiona pagos"
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    # actions = None
    list_display = ("cliente", "codigo", "periodo_inicio",
                    "periodo_final", "monto_formateado", "estado_pago")
    search_fields = ("usuario__nombre", "usuario__apellido", "usuario__vereda",
                     "codigo", "periodo_inicio")
    autocomplete_fields = ["usuario"]
    inlines = [PagoInline]

    def cliente(self, obj):
        return obj.usuario

    def estado_pago(self, obj):
        pago = obj.pagos.first()
        if pago:
            color = "green" if pago.estado == "pagado" else "orange"
            return format_html('<span style="color:{};">{}</span>', color, pago.estado.capitalize())
        return format_html('<span style="color:orange;">Pendiente</span>')

    estado_pago.short_description = "Estado del pago"
    estado_pago.admin_order_field = 'pagos__estado_pago'

    def monto_formateado(self, obj):
        return f"{obj.monto_a_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    monto_formateado.short_description = 'Valor a pagar'
    monto_formateado.admin_order_field = 'monto_a_pagar'


@admin.register(DetalleFactura)
class DetallePagoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("factura",)


admin_site.register(Factura, FacturaAdmin)
