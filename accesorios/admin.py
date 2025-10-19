from django.contrib import admin
from .models import Accesorio, ReporteFaltante, Reposicion, HistorialAccesorio

@admin.register(Accesorio)
class AccesorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_total', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')
    list_editable = ('cantidad_total',)
    search_fields = ('nombre', 'descripcion')
    list_filter = ('cantidad_total', 'fecha_creacion', 'creado_por')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    ordering = ('nombre',)

@admin.register(ReporteFaltante)
class ReporteFaltanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'accesorio', 'cantidad_faltante', 'estado', 'fecha_reporte', 'empleado_reporte')
    list_filter = ('estado', 'fecha_reporte', 'accesorio')
    search_fields = ('accesorio__nombre', 'empleado_reporte__username')
    readonly_fields = ('fecha_reporte',)
    ordering = ('-fecha_reporte',)

@admin.register(Reposicion)
class ReposicionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_accesorio', 'cantidad_comprada', 'fecha_compra', 'administrador')
    list_filter = ('fecha_compra',)
    search_fields = ('reporte__accesorio__nombre', 'administrador__username')
    readonly_fields = ('fecha_compra',)
    ordering = ('-fecha_compra',)
    
    def get_accesorio(self, obj):
        return obj.reporte.accesorio.nombre
    get_accesorio.short_description = 'Accesorio'

@admin.register(HistorialAccesorio)
class HistorialAccesorioAdmin(admin.ModelAdmin):
    list_display = ('accesorio_nombre', 'accion', 'usuario', 'fecha')
    list_filter = ('accion', 'fecha', 'usuario')
    search_fields = ('accesorio_nombre', 'usuario__username')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)
    
    def has_add_permission(self, request):
        # No permitir agregar manualmente desde el admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # No permitir modificar desde el admin
        return False
