from django.db import models
from django.contrib.auth.models import User

# --- Modelo de Perfil (Único Modelo en esta App) ---

class Profile(models.Model):
    ROLES = [
        ('Administrador', 'Administrador'),
        ('Entrenador', 'Entrenador'),
        ('Socio', 'Socio'),
    ]
    
    # Relación uno a uno con el usuario de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile') 
    telefono = models.CharField(max_length=30, blank=True, null=True) 
    
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='Socio',
        verbose_name="Rol de Usuario"
    ) 
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    def __str__(self): 
        return f'Perfil de {self.user.username} ({self.rol})'

# NOTA: Los modelos Plan, Membresia, Clase y Rutina han sido movidos a la app 'gestion'.