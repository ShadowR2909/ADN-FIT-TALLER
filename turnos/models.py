from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User # Asumo que esta es la forma correcta de importar tu modelo User
from django.db.models import Q

# Capacidad máxima del gimnasio por día
CAPACIDAD_MAXIMA_DIARIA = 50

class Turno(models.Model):
    # Opciones de estado del turno
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Validación'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado por Socio'),
        ('FINALIZADO', 'Finalizado (Asistido)'),
    ]

    socio = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='turnos',
        null=True,
        blank=True
    )
    
    # Ambos campos son obligatorios y consistentes
    hora_inicio = models.DateTimeField(verbose_name="Fecha/Hora de Inicio")
    hora_fin = models.DateTimeField(verbose_name="Fecha/Hora de Fin") 

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Turno de Gimnasio"
        verbose_name_plural = "Turnos de Gimnasio"
        # Usa el campo renombrado
        ordering = ['hora_inicio'] 

    def __str__(self):
        socio_nombre = self.socio.username if self.socio else 'Cupo Libre'
        # Usa el campo renombrado
        return f"Turno de {socio_nombre} el {self.hora_inicio.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """
        Validación a nivel de modelo antes de guardar.
        """
        super().clean()

        # Validación 1: El tiempo de fin debe ser posterior al inicio
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        
        # Validación 2: No se permiten reservas en el pasado
        if self.hora_inicio and self.hora_inicio < timezone.now():
             # Permite editar turnos pasados solo si ya están finalizados o cancelados
             if not self.pk or self.estado not in ['FINALIZADO', 'CANCELADO']:
                 raise ValidationError("No se puede crear o modificar un turno con fecha en el pasado.")


        # Validación 3: Lógica de solapamiento para el mismo socio (Solo para CONFIRMADOS/PENDIENTES)
        if self.socio and self.estado in ['CONFIRMADO', 'PENDIENTE']:
            # Filtra por turnos del mismo socio que estén activos
            turnos_activos = Turno.objects.filter(
                socio=self.socio,
                estado__in=['CONFIRMADO', 'PENDIENTE']
            ).exclude(pk=self.pk) # Excluye el turno actual si es una edición

            # Verifica si el nuevo turno se solapa (Inicio A < Fin B) AND (Fin A > Inicio B)
            solapamiento = turnos_activos.filter(
                hora_inicio__lt=self.hora_fin, 
                hora_fin__gt=self.hora_inicio
            )
            
            if solapamiento.exists():
                raise ValidationError("Ya tienes un turno activo que se solapa con este horario.")

        # Validación 4: Capacidad máxima por día (ajustada para el nuevo nombre de campo)
        # Contar cuántos turnos CONFIRMADOS o PENDIENTES hay para la fecha de inicio
        if self.hora_inicio:
            fecha_del_turno = self.hora_inicio.date()

            cupos_ocupados = Turno.objects.filter(
                # Usa el campo renombrado
                hora_inicio__date=fecha_del_turno
            ).exclude(
                estado__in=['CANCELADO', 'FINALIZADO']
            )

            if self.pk:
                cupos_ocupados = cupos_ocupados.exclude(pk=self.pk)

            if cupos_ocupados.count() >= CAPACIDAD_MAXIMA_DIARIA:
                raise ValidationError({
                    'hora_inicio': f'El día {fecha_del_turno} ha alcanzado su capacidad máxima de {CAPACIDAD_MAXIMA_DIARIA} turnos.'
                })


    def save(self, *args, **kwargs):
        """ Sobreescribe save para ejecutar clean antes de guardar. """
        self.full_clean()
        super().save(*args, **kwargs)

# Modelo auxiliar (se mantiene igual, ya que no se usa en la validación principal)
class CapacidadDiaria(models.Model):
    fecha = models.DateField(unique=True)
    capacidad = models.IntegerField(default=CAPACIDAD_MAXIMA_DIARIA, verbose_name="Cupos Máximos")

    def __str__(self):
        return f"Capacidad para {self.fecha}: {self.capacidad}"