from django.urls import path
from . import views

app_name = 'accesorios'

urlpatterns = [
    # Proceso de consulta/listado
    path('inventario/', views.inventario_list, name='inventario_list'),
    
    # Proceso de agregar nuevo accesorio
    path('crear/', views.accesorio_create, name='accesorio_create'),
    
    # Proceso de editar accesorio existente
    path('editar/<int:pk>/', views.accesorio_update, name='accesorio_update'),
    
    # Proceso de eliminar accesorio
    path('eliminar/<int:pk>/', views.accesorio_delete, name='accesorio_delete'),
    
    # Proceso de reportar faltante (Crear reporte)
    path('reportar/', views.reporte_faltante_create, name='reporte_faltante_create'),
    
    # Proceso de confirmación (Empleados/Admin)
    path('reportes/', views.reportes_pendientes_list, name='reportes_pendientes'),
    path('reportes/confirmar/<int:pk>/', views.reporte_confirmar, name='reporte_confirmar'),

    path('reposicion/crear/<int:pk>/', views.reposicion_create, name='reposicion_create'), 

    # Historial de reportes y reposiciones
    path('reportes/historial/', views.historial_accesorios, name='historial_accesorios'),


]