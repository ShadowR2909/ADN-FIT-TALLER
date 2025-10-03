# cuentas/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 1. Autenticación (El login es la página de inicio para NO logueados)
    path("", views.login_view, name="login"), # <-- Login ahora en la ruta raíz
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    
    # 2. Dashboard (Ahora tiene una ruta específica, accesible solo logueado)
    path("dashboard/", views.dashboard, name="dashboard"), 
    
    # Perfil y Socio
    path("perfil/", views.editar_perfil, name="editar_perfil"),
    path("mi-plan/", views.mi_plan_view, name="mi_plan"),
    path("mis-clases/", views.mis_clases, name="mis_clases"),
    path("mi-rutina/", views.mi_rutina_view, name="mi_rutina"),
    path('mi-membresia/', views.mi_membresia, name='mi_membresia'),

    
    # Entrenador/Admin
    path("alumnos/", views.lista_alumnos, name="lista_alumnos"),
    path("asignar-rutinas/", views.asignar_rutinas_view, name="asignar_rutinas"),
    path("gestion-usuarios/", views.gestion_usuarios, name="gestion_usuarios"),
]