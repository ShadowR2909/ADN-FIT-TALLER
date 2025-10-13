from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    # --- RUTAS PARA SOCIOS ---
    
    # 1. Vista principal para el socio: Muestra los turnos DISPONIBLES para reservar.
    # URL: /turnos/
    path('', views.TurnosDisponiblesView.as_view(), name='disponibles'), 
    
    # 2. Lista de turnos que el socio ya tiene reservados.
    # URL: /turnos/mis-reservas/
    path('mis-reservas/', views.TurnosMisReservasView.as_view(), name='mis_reservas'), 
    
    # 3. Acción POST para que el socio tome un turno disponible.
    # URL: /turnos/reservar/<int:pk>/
    path('reservar/<int:pk>/', views.TomarTurnoView.as_view(), name='tomar_turno'), 
    
    # 4. Acción para que el socio cancele uno de sus turnos.
    # URL: /turnos/<int:pk>/cancelar/
    path('<int:pk>/cancelar/', views.TurnoCancelView.as_view(), name='cancelar'), 

    # --- RUTAS PARA STAFF/ADMIN ---
    
    # 5. Lista de todos los turnos (Gestión y administración).
    # URL: /turnos/staff/
    path('staff_list/', views.StaffTurnoListView.as_view(), name='staff_list'), 
    
    # 6. Crear nuevo cupo de turno (que el socio puede tomar).
    # URL: /turnos/staff/crear/
    path('staff/crear/', views.TurnoCreationStaffView.as_view(), name='staff_create'),

    # 7. Vista de edición (solo Staff).
    # URL: /turnos/staff/<int:pk>/editar/
    path('staff/<int:pk>/editar/', views.TurnoUpdateView.as_view(), name='turno_update'),
]