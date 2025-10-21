# proveedores/models.py

from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Proveedor")
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")

    activo = models.BooleanField(default=True, verbose_name="Estado Activo")
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre