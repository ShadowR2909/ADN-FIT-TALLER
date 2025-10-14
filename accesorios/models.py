from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

# Asume que ya tienes un modelo de Usuario extendido o Profile
User = settings.AUTH_USER_MODEL 

class Accesorio(models.Model):
    """Representa un accesorio físico del gimnasio (e.g., mancuerna, colchoneta)."""
    nombre = models.CharField(max_length=100, unique=True)
    cantidad_total = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad en Inventario"
    )
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Accesorios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_total} en stock)"

class ReporteFaltante(models.Model):
    """
    Representa el reporte de un empleado sobre la falta de un accesorio.
    Esto se corresponde con el flujo 'Faltante' y 'Reporte' en el DFD.
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Confirmación'),
        ('CONFIRMADO', 'Confirmado (Requiere Compra)'),
        ('DESCARTADO', 'Descartado por Empleado/Admin'),
    ]

    accesorio = models.ForeignKey(Accesorio, on_delete=models.CASCADE)
    cantidad_faltante = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Unidades faltantes reportadas"
    )
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    
    # El Empleado que crea el reporte
    empleado_reporte = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reportes_creados'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE'
    )
    
    # Campo para la confirmación del flujo (Confirmacion/Confirma faltante)
    empleado_confirmacion = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reportes_confirmados'
    )
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Reporte de Faltante"
        verbose_name_plural = "Reportes de Faltantes"
        ordering = ['-fecha_reporte']

    def __str__(self):
        return f"Reporte #{self.id} de {self.accesorio.nombre} - {self.estado}"

class Reposicion(models.Model):
    """Registra la compra o reposición de stock en respuesta a un ReporteFaltante confirmado."""
    
    # Vinculamos al reporte que generó la necesidad
    reporte = models.OneToOneField(
        ReporteFaltante, 
        on_delete=models.CASCADE,
        limit_choices_to={'estado': 'CONFIRMADO'}, # Solo se puede reponer un reporte confirmado
        related_name='reposicion'
    )
    
    # Cantidad que se compró (debería ser igual o mayor a la faltante)
    cantidad_comprada = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de unidades compradas"
    )
    
    fecha_compra = models.DateTimeField(auto_now_add=True)
    
    # El Administrador que procesó la compra
    administrador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='compras_procesadas'
    )
    
    def __str__(self):
        return f'Reposición de {self.cantidad_comprada} de {self.reporte.accesorio.nombre}'

    class Meta:
        verbose_name = "Reposición de Stock"
        verbose_name_plural = "Reposiciones de Stock"
        ordering = ['-fecha_compra']