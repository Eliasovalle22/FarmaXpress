from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo para empleados/administradores que ingresan al sistema
class User(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('inventario', 'Inventario'),
        ('contable', 'Contable'),
        ('compras', 'Compras'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='vendedor')
    telefono = models.CharField(max_length=15, blank=True, null=True)

    # Usar email como identificador único
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"