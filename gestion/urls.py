from django.urls import path
from . import views

urlpatterns = [
    # Gestión de Planes
    path('gestion/planes/', views.gestion_planes_view, name='gestion_planes'),
    path('gestion/planes/editar/<int:plan_id>/', views.editar_plan_view, name='editar_plan'),
    
    # Gestión de Membresías
    path('gestion/membresias/', views.gestion_membresias_view, name='gestion_membresias'),
    path('gestion/membresias/editar/<int:membresia_id>/', views.editar_membresia_view, name='editar_membresia'),
    
    # Gestión de Clases
    path('gestion/clases/', views.gestion_clases_view, name='gestion_clases'),
    path('gestion/clases/editar/<int:clase_id>/', views.editar_clase_view, name='editar_clase'),
    
    # REPORTES
    path('gestion/reportes/', views.reportes_view, name='reportes'), 

    # Nuevo:     GENERIC DELETE URL
    path('gestion/eliminar/<str:model_name>/<int:pk>/', views.eliminar_registro_view, name='eliminar_registro'),


]