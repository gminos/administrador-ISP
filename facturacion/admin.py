from django.contrib import admin
from .models import Factura, Pago, DetalleFactura
from base.admin import admin_site


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("usuario",)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("factura",)


@admin.register(DetalleFactura)
class DetallePagoAdmin(admin.ModelAdmin):
    list_display = ("factura",)

admin_site.register(Factura, FacturaAdmin)
admin_site.register(Pago, PagoAdmin)
admin_site.register(DetalleFactura, DetallePagoAdmin)
