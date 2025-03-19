from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    role = models.ForeignKey(
        'Rol', on_delete=models.SET_NULL, null=True, blank=True)
    sede = models.ForeignKey(
        'Sede', on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios (Admin)'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
