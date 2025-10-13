from django.contrib import admin
from .models import Turno, CapacidadDiaria

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    # Campos mostrados en la lista
    list_display = ('socio', 'fecha_hora_inicio', 'estado', 'cupo_disponible_hoy')

    # Filtros laterales
    list_filter = ('estado', 'fecha_hora_inicio')

    # Búsqueda
    search_fields = ('socio__username', 'socio__first_name')

    # Campos de solo lectura
    readonly_fields = ('creado_en',)

    # Campo personalizado para mostrar la disponibilidad
    def cupo_disponible_hoy(self, obj):
        fecha = obj.fecha_hora_inicio.date()
        # Reutiliza la lógica de validación para contar cupos (la exclusión de estados)
        cupos_ocupados = Turno.objects.filter(
            fecha_hora_inicio__date=fecha
        ).exclude(
            estado__in=['CANCELADO', 'FINALIZADO']
        ).count()
        capacidad = CapacidadDiaria.objects.filter(fecha=fecha).first()
        max_cupos = capacidad.capacidad if capacidad else 50
        return f"{cupos_ocupados} / {max_cupos}"
    cupo_disponible_hoy.short_description = "Cupos Ocupados (Día)"


@admin.register(CapacidadDiaria)
class CapacidadDiariaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'capacidad')
    search_fields = ('fecha',)
    ordering = ('fecha',)
