from django import forms
from django.contrib import admin
from .models import Intalacion


@admin.register(Intalacion)
class InstalacionAdmin(admin.ModelAdmin):
    list_display = ("documento", "nombre", "apellido", "fecha_instalacion", "costo")
    search_fields = ("usuario__documento", "usuario__nombre", "usuario__apellido")
    autocomplete_fields = ["usuario"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["usuario"].widget = forms.HiddenInput()
        return form

    def documento(self, obj):
        return obj.usuario.documento

    def nombre(self, obj):
        return obj.usuario.nombre

    def apellido(self, obj):
        return obj.usuario.apellido
