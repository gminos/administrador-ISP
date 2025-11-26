from django import forms
from django.contrib import admin
from .models import Intalacion
from base.admin import admin_site
from django.utils import timezone
from django.utils.formats import date_format

@admin.register(Intalacion)
class InstalacionAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        "cliente",
        "fecha_instalacion_cliente",
        "monto_formateado"
    )
    search_fields = ("cliente__nombre", "cliente__apellido")
    autocomplete_fields = ["cliente"]

    def get_form(self, request, obj=None, change=False ,**kwargs):
        form = super().get_form(request, obj, change=change,**kwargs)
        if obj:
            form.base_fields["cliente"].widget = forms.HiddenInput()
        return form

    @admin.display(description="nombre cliente")
    def cliente(self, obj):
        return obj.cliente

    @admin.display(description="monto formateado")
    def monto_formateado(self, obj):
        return f"{obj.costo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="fecha de instalacion")
    def fecha_instalacion_cliente(self, obj):
        fecha_local = timezone.localtime(obj.fecha_instalacion)
        return date_format(
            fecha_local, 
            format='j \\d\\e F \\d\\e Y \\a \\l\\a\\s H:i', 
            use_l10n=True
        )


admin_site.register(Intalacion, InstalacionAdmin)
