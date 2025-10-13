#turnos/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Turno

User= get_user_model()

class TurnoForm(forms.ModelForm):
    # CORRECCIÓN: CAMBIAR 'form' A 'forms'
    socio = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        label="Socio (Opcional - Staff)"
    )

    # Permite al usuario seleccionar solo la fecha y hora de inicio
    class Meta:
        model = Turno
        # Excluimos 'socio', 'estado' y 'creado_en' porque se manejan en la vista o el modelo
        fields = ['socio','fecha_hora_inicio','estado'] 
        widgets = {
            # Esto ayuda a usar un selector de fecha/hora en el HTML
            'fecha_hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def __init__(self, *args, **kwargs):
        # La vista debe pasar el usuario actual a través de kwargs
        self.request_user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        is_staff_or_admin = self.request_user.is_superuser or \
                            (self.request_user.profile.rol in ['Administrador', 'Entrenador'] if hasattr(self.request_user, 'profile') else False)

        if not is_staff_or_admin:
            # Si es un socio, elimina los campos 'socio' y 'estado' del formulario
            del self.fields['socio']
            del self.fields['estado']
        else:
            # Si es staff, oculta el campo 'estado' si es un nuevo turno
            # Si el staff crea el turno, el estado por defecto es PENDIENTE (gestionado en la vista)
            if 'socio' in self.fields:
                self.fields['socio'].required = False
  
    def clean_fecha_hora_inicio(self):
        # Reutilizamos la lógica de validación de cupos que ya está en el modelo (Turno.clean)
        return self.cleaned_data['fecha_hora_inicio']
