# proveedores/urls.py

from django.urls import path
from . import views

app_name = 'proveedores' 

urlpatterns = [
    # C - Crear
    path('crear/', views.ProveedorCreateView.as_view(), name='proveedor_create'), 
    
    # R - Lista (Activos, Inactivos, Todos)
    path('', views.ProveedorListView.as_view(), name='proveedor_list'), 
    
    # R - Detalle
    path('<int:pk>/', views.ProveedorDetailView.as_view(), name='proveedor_detail'),
    
    # U - Actualizar
    path('<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    
    # D - Desactivar/Activar (Reemplaza a la vista de eliminación)
    # ESTA LÍNEA DEBE EXISTIR Y SER EXACTA:
    path('<int:pk>/estado/', views.toggle_proveedor_status, name='proveedor_toggle_status'), 
]