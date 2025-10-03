from django.db import models
from django.contrib.auth.models import User 

# --- Modelos de Gestión del Gimnasio ---

class Plan(models.Model):
    """Representa los diferentes planes de membresía."""
    NOMBRE_PLANES = [
        ('BASICO', 'Básico'),
        ('PREMIUM', 'Premium'),
        ('VIP', 'VIP'),
    ]
    nombre = models.CharField(max_length=50, choices=NOMBRE_PLANES, unique=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    duracion_dias = models.IntegerField(default=30)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.nombre} (${self.precio})'

class Membresia(models.Model):
    """Relaciona un Socio con un Plan y lleva registro de su estado."""
    socio = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'profile__rol': 'Socio'}, 
        related_name='gestion_membresia' # related_name ÚNICO
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'Membresía de {self.socio.username} - {self.plan.nombre}'

class Clase(models.Model):
    """Define las clases grupales disponibles."""
    DIAS_SEMANA = [
        ('LU', 'Lunes'), ('MA', 'Martes'), ('MI', 'Miércoles'),
        ('JU', 'Jueves'), ('VI', 'Viernes'), ('SA', 'Sábado'),
    ]
    nombre = models.CharField(max_length=100)
    dia_semana = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    entrenador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'profile__rol__in': ['Entrenador', 'Administrador']},
        related_name='gestion_clases_impartidas' # related_name ÚNICO
    )
    capacidad = models.IntegerField(default=20)

    def __str__(self):
        return f'{self.nombre} ({self.get_dia_semana_display()}) a las {self.hora_inicio}'
    
    class Meta:
        unique_together = ('nombre', 'dia_semana', 'hora_inicio') 


class Rutina(models.Model):
    """Representa una rutina de ejercicios asignada por un Entrenador a un Socio."""
    socio = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'profile__rol': 'Socio'},
        related_name='gestion_rutinas_asignadas' # related_name ÚNICO
    )
    entrenador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'profile__rol__in': ['Entrenador', 'Administrador']},
        related_name='gestion_rutinas_creadas' # related_name ÚNICO
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_asignacion = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f'Rutina "{self.nombre}" para {self.socio.username}'