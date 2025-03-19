from django.db import models

# Create your models here.


class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    rol = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.rol
