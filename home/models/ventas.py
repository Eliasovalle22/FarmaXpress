from django.db import models

class Venta(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    sede = models.ForeignKey('Sede', on_delete=models.CASCADE)
    vendedor = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True)  # Opcional
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def actualizar_total(self):
        total = self.detalleventa_set.aggregate(models.Sum('subtotal'))['subtotal__sum'] or 0
        self.total = total
        self.save()
        
        class Meta:
            db_table = 'ventas'
            verbose_name = 'Venta'
            verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta {self.id} - {self.sede} ({self.fecha_hora})"


    
# Modelo para detalles de venta
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        self.venta.actualizar_total()
        
        class Meta:
            db_table = 'detalle_ventas' 
            verbose_name = 'Detalle de Venta'
            verbose_name_plural = 'Detalles de Venta'

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
    
    
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