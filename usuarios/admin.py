from django import forms
from django.contrib import admin
from planes.models import UsuarioPlan
from instalaciones.models import Intalacion
from .models import Usuario, Direccion


class InstalacionInline(admin.TabularInline):
    model = Intalacion
    extra = 0


class UsuarioPlanInline(admin.TabularInline):
    model = UsuarioPlan
    extra = 0


# Crear direcciones al momento de crear un usuario
class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "apellido",
        "telefono",
    )
    inlines = [
        DireccionInline,
        InstalacionInline,
        UsuarioPlanInline,
    ]
    search_fields = (
        "nombre",
        "apellido",
    )


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "apellido",
        "vereda",
        "descripcion",
    )
    search_fields = (
        "vereda",
        "usuario__nombre",
        "usuario__apellido",
    )
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
