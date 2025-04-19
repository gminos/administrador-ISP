from django.db import models


# tabla usuarios. por defecto defecto los campos son not null (no hay que expecificar)
class Usuario(models.Model):
    documento = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.documento} - {self.nombre} - {self.apellido}"

    class Meta:
        verbose_name = "agregar usuario"
        verbose_name_plural = "agregar usuarios"


# Tabla Direccion para llevar el control de todas las direciones posibles del usuario
class Direccion(models.Model):
    direcciones_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "Usuario", on_delete=models.CASCADE, related_name="direcciones"
    )
    vereda = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Vereda: {self.vereda} Documento: {self.usuario.documento} Nombre: {self.usuario.nombre}"

    class Meta:
        verbose_name = "agregar direccion"
        verbose_name_plural = "agregar direcciones"
