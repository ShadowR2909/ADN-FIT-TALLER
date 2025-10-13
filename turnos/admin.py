from django.contrib import admin
from .models import Turno, CapacidadDiaria # Asegúrate de que los modelos están correctamente importados

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    # 🚨 CORRECCIÓN 1: Reemplazar 'fecha_hora_inicio' por 'hora_inicio' y agregar 'hora_fin'
    list_display = ('socio', 'hora_inicio', 'hora_fin', 'estado', 'cupo_disponible_hoy')

    # 🚨 CORRECCIÓN 2: Reemplazar 'fecha_hora_inicio' por 'hora_inicio' en list_filter
    list_filter = ('estado', 'hora_inicio') # Puedes usar 'hora_inicio__date' si quieres filtrar solo por día

    # Búsqueda
    search_fields = ('socio__username', 'socio__first_name')

    # Campos de solo lectura
    readonly_fields = ('creado_en',)

    # 🚨 CORRECCIÓN 3: Actualizar la función personalizada para usar 'hora_inicio'
    def cupo_disponible_hoy(self, obj):
        # Usamos hora_inicio para obtener la fecha del turno
        fecha = obj.hora_inicio.date() 
        
        # Contar cuántos turnos activos hay para esa fecha
        cupos_ocupados = Turno.objects.filter(
            hora_inicio__date=fecha # 🚨 CORRECCIÓN: Filtrar por el nuevo campo
        ).exclude(
            estado__in=['CANCELADO', 'FINALIZADO']
        ).count()
        
        # Obtener capacidad máxima
        capacidad = CapacidadDiaria.objects.filter(fecha=fecha).first()
        max_cupos = capacidad.capacidad if capacidad else 50
        
        return f"{cupos_ocupados} / {max_cupos}"
    cupo_disponible_hoy.short_description = "Cupos Ocupados (Día)"


@admin.register(CapacidadDiaria)
class CapacidadDiariaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'capacidad')
    search_fields = ('fecha',)
    ordering = ('fecha',)