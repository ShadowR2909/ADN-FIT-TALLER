
from django.contrib import admin
from django.urls import path, include
from cuentas import views as cuentas_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path ('', include ('cuentas.urls')),    #Vistas de autenticacion y perfil
    path('', include('gestion.urls')),      #vistas de gestion de negocio
    path('accounts/', include('django.contrib.auth.urls')), 

    
]
