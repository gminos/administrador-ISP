from django import forms
from django.contrib import admin
from .models import Intalacion
from base.admin import admin_site


@admin.register(Intalacion)
class InstalacionAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        "cliente",
        "fecha_instalacion",
        "monto_formateado"
    )
    search_fields = ("usuario__nombre", "usuario__apellido")
    autocomplete_fields = ["usuario"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["usuario"].widget = forms.HiddenInput()
        return form

    def cliente(self, obj):
        return obj.usuario

    def monto_formateado(self, obj):
        return f"{obj.costo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    monto_formateado.short_description = 'Valor'


admin_site.register(Intalacion, InstalacionAdmin)
