from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_sede1 = models.IntegerField(default=0)
    stock_sede2 = models.IntegerField(default=0)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    fecha_baja = models.DateTimeField(blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True)
    imagen = models.ImageField(
        upload_to='productos/', blank=True, null=True)

    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def stock_total(self):
        return self.stock_sede1 + self.stock_sede2

    def is_low_stock(self):
        return self.stock_sede1 < 5 or self.stock_sede2 < 5

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
