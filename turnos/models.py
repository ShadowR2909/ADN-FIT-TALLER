#turnos/models.py 
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User

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

    # Asume que tienes un modelo de Usuario/Socio en 'cuentas'
    # Si el modelo de usuario está en 'cuentas.models.Socio', ajusta 'cuentas.Socio'
    socio = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='turnos',
        null=True,
        blank=True
    )
    fecha_hora_inicio = models.DateTimeField(verbose_name="Fecha y Hora de Inicio")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Turno de Gimnasio"
        verbose_name_plural = "Turnos de Gimnasio"
        ordering = ['fecha_hora_inicio']

    def __str__(self):
        # Muestra el socio, la fecha y el estado del turno
        return f"Turno de {self.socio.username} el {self.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """
        Validación a nivel de modelo antes de guardar.
        Asegura que no se exceda la capacidad máxima diaria.
        """
        super().clean()

        # 1. Asegurar que la fecha sea en el futuro (no se pueden reservar turnos pasados)
        if self.fecha_hora_inicio < timezone.now():
            raise ValidationError('No se puede reservar un turno en el pasado.')

        # 2. Validar capacidad máxima por día
        fecha_del_turno = self.fecha_hora_inicio.date()

        # Contar cuántos turnos CONFIRMADOS o PENDIENTES hay para esa fecha
        cupos_ocupados = Turno.objects.filter(
            fecha_hora_inicio__date=fecha_del_turno
        ).exclude(
            estado__in=['CANCELADO', 'FINALIZADO'] # No contamos cancelados o finalizados
        )

        # Si estamos editando un turno existente, lo excluimos de la cuenta
        if self.pk:
            cupos_ocupados = cupos_ocupados.exclude(pk=self.pk)

        if cupos_ocupados.count() >= CAPACIDAD_MAXIMA_DIARIA:
            raise ValidationError({
                'fecha_hora_inicio': f'El día {fecha_del_turno} ha alcanzado su capacidad máxima de {CAPACIDAD_MAXIMA_DIARIA} turnos.'
            })

    def save(self, *args, **kwargs):
        """
        Sobreescribe save para ejecutar clean antes de guardar.
        """
        self.full_clean()  # Llama a clean() y valida campos
        super().save(*args, **kwargs)

# Modelo auxiliar para gestionar la capacidad diaria si fuera dinámica
class CapacidadDiaria(models.Model):
    fecha = models.DateField(unique=True)
    capacidad = models.IntegerField(default=CAPACIDAD_MAXIMA_DIARIA, verbose_name="Cupos Máximos")

    def __str__(self):
        return f"Capacidad para {self.fecha}: {self.capacidad}"
