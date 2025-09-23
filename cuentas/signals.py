from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Profile

@receiver(post_save, sender=User)
def crear_o_actualizar_perfil(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@receiver(post_save, sender=User)
def asignar_grupo_usuario(sender, instance, created, **kwargs):
    if created:
        grupos = ['Administrador', 'Entrenadores', 'Socios']
        for nombre in grupos:
            Group.objects.get_or_create(name=nombre)
        
        grupo_socio = Group.objects.get(name='Socios')
        instance.groups.add(grupo_socio)