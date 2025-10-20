from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

# ----------------------------------------------------
# 🚨 SEÑALES PARA CREACIÓN AUTOMÁTICA DEL PERFIL 🚨
# ----------------------------------------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un objeto Profile automáticamente cuando se crea un User."""
    if created:
        # El campo 'rol' se inicializa con el valor 'Socio' por defecto del modelo
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el objeto Profile cuando se guarda el User."""
    instance.profile.save()


    