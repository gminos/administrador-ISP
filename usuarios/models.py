from django.db import models


# tabla usuarios. por defecto defecto los campos son not null (no hay que expecificar)
class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10)
    vereda = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "Agrega o modifica clientes"


# Tabla Direccion para llevar el control de todas las direciones posibles del usuario
# class Direccion(models.Model):
#     direcciones_id = models.AutoField(primary_key=True)
#     usuario = models.ForeignKey(
#         "Usuario", on_delete=models.CASCADE, related_name="direcciones"
#     )
#     vereda = models.CharField(max_length=20)
#     descripcion = models.TextField(blank=True, null=True)
#
#     def __str__(self):
#         return f"Informacion {self.usuario.nombre} {self.usuario.apellido}"
#
#     class Meta:
#         verbose_name = "direccion a cliente"
#         verbose_name_plural = "crear/Editar direccion de cliente"
