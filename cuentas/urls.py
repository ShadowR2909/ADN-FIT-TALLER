from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),           # login personalizado
    path("register/", views.register, name="register"),      # registro
    path("dashboard/", views.dashboard, name="dashboard"),   # dashboard general
    path("editar-perfil/", views.editar_perfil, name="editar_perfil"),  # editar perfil

    # páginas según rol
    path("mis-clases/", views.mis_clases, name="mis_clases"),
    path("lista-alumnos/", views.lista_alumnos, name="lista_alumnos"),
    path("gestion-usuarios/", views.gestion_usuarios, name="gestion_usuarios"),

    # logout usando la vista de Django (acepta GET)
    path('logout/', LogoutView.as_view(), name='logout'),
]
