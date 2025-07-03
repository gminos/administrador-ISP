from django import forms
from django.contrib import admin
from .models import Intalacion
from base.admin import admin_site


@admin.register(Intalacion)
class InstalacionAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("nombre", "apellido", "fecha_instalacion", "costo")
    search_fields = ("usuario__nombre", "usuario__apellido")
    autocomplete_fields = ["usuario"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["usuario"].widget = forms.HiddenInput()
        return form

    def nombre(self, obj):
        return obj.usuario.nombre

    def apellido(self, obj):
        return obj.usuario.apellido


admin_site.register(Intalacion, InstalacionAdmin)
