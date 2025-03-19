from django.db import models


class Sede(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        db_table = 'sedes'
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'

    def __str__(self):
        return self.nombre
