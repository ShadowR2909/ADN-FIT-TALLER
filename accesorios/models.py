from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

User = settings.AUTH_USER_MODEL

# 1. Accesorio primero
class Accesorio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    cantidad_total = models.PositiveIntegerField(default=0, verbose_name="Cantidad en Inventario")
    descripcion = models.TextField(blank=True, null=True)
    
    # Soft delete
    activo = models.BooleanField(default=True)  # <--- esto es lo nuevo
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='accesorios_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accesorios_modificados')
    fecha_modificacion = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Accesorios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_total} en stock)"


class HistorialAccesorio(models.Model):
    ACCIONES = [
        ('CREADO', 'Accesorio Creado'),
        ('EDITADO', 'Accesorio Editado'),
        ('ELIMINADO', 'Accesorio Eliminado'),
    ]
    accesorio_nombre = models.CharField(max_length=100)
    accesorio_id = models.PositiveIntegerField(null=True, blank=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Historial de Accesorio"
        verbose_name_plural = "Historial de Accesorios"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.accion} - {self.accesorio_nombre} por {self.usuario} ({self.fecha})"


class ReporteFaltante(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Confirmación'),
        ('CONFIRMADO', 'Confirmado (Requiere Compra)'),
        ('DESCARTADO', 'Descartado por Empleado/Admin'),
    ]
    accesorio = models.ForeignKey('Accesorio', on_delete=models.CASCADE)
    cantidad_faltante = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    empleado_reporte = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reportes_creados')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    empleado_confirmacion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes_confirmados')
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Reporte de Faltante"
        verbose_name_plural = "Reportes de Faltantes"
        ordering = ['-fecha_reporte']

    def __str__(self):
        return f"Reporte #{self.id} de {self.accesorio.nombre} - {self.estado}"

class Reposicion(models.Model):
    reporte = models.OneToOneField('ReporteFaltante', on_delete=models.CASCADE, related_name='reposicion')
    cantidad_comprada = models.PositiveIntegerField(default=0, verbose_name="Cantidad de unidades compradas")
    fecha_compra = models.DateTimeField(auto_now_add=True)
    administrador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='compras_procesadas')

    class Meta:
        verbose_name = "Reposición de Stock"
        verbose_name_plural = "Reposiciones de Stock"
        ordering = ['-fecha_compra']

    def __str__(self):
        return f'Reposición de {self.cantidad_comprada} de {self.reporte.accesorio.nombre}'
