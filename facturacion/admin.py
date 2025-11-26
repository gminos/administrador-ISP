from django.contrib import admin
from .models import Factura, Pago
from base.admin import admin_site
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.db.models import Sum

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
    list_filter = (MesFiltro,)
    ordering = ("periodo_inicio__month","cliente__vereda", "cliente__nombre",)
    list_per_page = 60

    @admin.display(description="cliente")
    def cliente(self, obj):
        return f'{obj.cliente.nombre} {obj.cliente.apellido}'

    @admin.display(description="estado del pago")
    def estado_pago(self, obj):
        pago = obj.pagos.filter(tipo_pago="mensualidad").first()
        if pago:
            color = "green" if pago.estado == "pagado" else "red"
            estado = pago.estado.capitalize()
        else:
            color = "red"
            estado = "Pendiente"
        return format_html('<span style="color:{};">{}</span>', color, estado)

    @admin.display(description="total pagado")
    def total_pagado(self, obj):
        total = obj.pagos.filter(estado="pagado").aggregate(
        Sum("monto_pagado")
        )["monto_pagado__sum"] or 0
        return "{:,.2f}".format(total).replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="fecha de pago")
    def fecha_pago(self, obj):
        pago = obj.pagos.filter(tipo_pago="mensualidad", estado="pagado").first()
        if pago:
            fecha = pago.fecha_pago
            dia = fecha.day
            mes = MESES[fecha.month]
            year = fecha.year
            return f"{dia} de {mes} - {year}"
        return "Sin pago registrado"

    @admin.display(description="vereda")
    def cliente_vereda(self, obj):
        return obj.cliente.vereda

    @admin.display(description="periodo facturado")
    def periodo_facturado(self, obj):
        dia_inicio = obj.periodo_inicio.day
        dia_final = obj.periodo_final.day
        mes = MESES[obj.periodo_final.month].capitalize()
        return f"{dia_inicio} ~ {dia_final} {mes}"

    @admin.display(description="fecha reconexion")
    def fecha_reconexion_formateada(self, obj):
        dia_reconexion = obj.fecha_reconexion.day
        mes_reconexion = MESES[obj.fecha_reconexion.month].capitalize()
        return f"{dia_reconexion} {mes_reconexion}"


admin_site.register(Factura, FacturaAdmin)
