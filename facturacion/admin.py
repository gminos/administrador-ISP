from django.contrib import admin
from .models import Factura, Pago, DetalleFactura
from base.admin import admin_site


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("cliente", "codigo", "periodo_inicio",
                    "periodo_final", "monto_a_pagar")
    search_fields = ("usuario__nombre", "usuario__apellido", "codigo")
    autocomplete_fields = ["usuario"]

    def cliente(self, obj):
        return obj.usuario


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        "factura",
        "estado",
        "fecha_pago",
        "metodo")
    search_fields = ("usuario__nombre", "usuario__apellido")


@admin.register(DetalleFactura)
class DetallePagoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("factura",)


admin_site.register(Factura, FacturaAdmin)
admin_site.register(Pago, PagoAdmin)
admin_site.register(DetalleFactura, DetallePagoAdmin)
