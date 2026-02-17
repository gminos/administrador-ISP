from django.contrib import admin
from unfold.admin import ModelAdmin
from facturacion.models import Factura, Pago
from base.admin import admin_site
from django.utils.html import format_html
from django.db.models import Sum
from django.utils.formats import date_format
from datetime import date
from django.db import models
from unfold.widgets import UnfoldAdminDateWidget, UnfoldAdminSingleDateWidget


class PagoInline(admin.TabularInline):
    model = Pago
    verbose_name_plural = "Gestiona pagos"
    extra = 0
    formfield_overrides = {
        models.DateField: {"widget": UnfoldAdminDateWidget},
    }
    

@admin.register(Factura)
class FacturaAdmin(ModelAdmin):
    formfield_overrides = {
        models.DateField: {"widget": UnfoldAdminDateWidget},
    }
    list_select_related = ["cliente"]
    actions = None
    list_display = (
        "cliente",
        "cliente_vereda",
        "estado_pago",
        "fecha_pago",
        "total_pagado",
        "periodo_facturado",
        "fecha_reconexion_formateada",
    )
    search_fields = ("cliente__nombre", "cliente__apellido")
    autocomplete_fields = ["cliente"]
    inlines = [PagoInline]
    date_hierarchy = "periodo_final"
    ordering = ("periodo_inicio__month","cliente__vereda", "cliente__nombre",)
    list_per_page = 70

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("pagos")

    @admin.display(description="cliente")
    def cliente(self, obj):
        return f'{obj.cliente.nombre} {obj.cliente.apellido}'

    @admin.display(description="estado del pago")
    def estado_pago(self, obj):
        pagos_mensualidad = [p for p in obj.pagos.all() if p.tipo_pago == "mensualidad"]
        pago = pagos_mensualidad[0] if pagos_mensualidad else None
        
        if pago:
            color = "green" if pago.estado == "pagado" else "red"
            estado = pago.estado.capitalize()
        else:
            color = "red"
            estado = "Pendiente"
        return format_html('<span style="color:{};">{}</span>', color, estado)

    @admin.display(description="total pagado")
    def total_pagado(self, obj):
        total = sum(p.monto_pagado for p in obj.pagos.all() if p.estado == "pagado")
        return "{:,.2f}".format(total).replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="fecha de pago")
    def fecha_pago(self, obj):
        pagos_pagados = [p for p in obj.pagos.all() if p.tipo_pago == "mensualidad" and p.estado == "pagado"]
        pago = pagos_pagados[0] if pagos_pagados else None
        
        if pago:
            fecha = pago.fecha_pago
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


admin_site.register(Factura, FacturaAdmin)
