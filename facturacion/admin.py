from django.contrib import admin
from .models import Factura, Pago, DetalleFactura
from base.admin import admin_site


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    # actions = None
    list_display = ("cliente", "codigo", "periodo_inicio",
                    "periodo_final", "monto_a_pagar", "estado_pago")
    search_fields = ("usuario__nombre", "usuario__apellido", "usuario__vereda",
                     "codigo", "periodo_inicio")
    autocomplete_fields = ["usuario"]
    inlines = [PagoInline]

    def cliente(self, obj):
        return obj.usuario

    def estado_pago(self, obj):
        pago = obj.pagos.first()
        if pago:
            return pago.estado.capitalize()
        return "Pendiente"  # por defecto si no se ha creado el pago aún
    estado_pago.short_description = "Estado del pago"

# @admin.register(Pago)
# class PagoAdmin(admin.ModelAdmin):
    # actions = None
    # list_display = (
    #     "factura"
    #     "estado",
    #     "fecha_pago",
    #     "metodo")


@admin.register(DetalleFactura)
class DetallePagoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("factura",)


admin_site.register(Factura, FacturaAdmin)
# admin_site.register(Pago, PagoAdmin)
# admin_site.register(DetalleFactura, DetallePagoAdmin)
