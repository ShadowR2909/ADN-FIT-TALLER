from django import forms
from django.contrib.auth import get_user_model
from .models import Turno

User = get_user_model()

class TurnoForm(forms.ModelForm):
    # Campo socio visible solo para Staff para asignar directamente.
    socio = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        label="Socio (Opcional - Staff)"
    )

    class Meta:
        model = Turno
        # 🚨 CAMPOS CORREGIDOS: Incluye hora_inicio y hora_fin
        fields = ['socio','hora_inicio','hora_fin','estado'] 
        widgets = {
            # Uso de datetime-local para ambos campos de fecha y hora
            'hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
            'hora_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
        }

    def __init__(self, *args, **kwargs):
        # La vista debe pasar el usuario actual a través de kwargs
        self.request_user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        # Lógica para determinar si el usuario es Staff o Admin (ajusta según tu lógica de perfiles)
        is_staff_or_admin = self.request_user.is_superuser or \
                             (self.request_user.profile.rol in ['Administrador', 'Entrenador'] if hasattr(self.request_user, 'profile') else False)

        if not is_staff_or_admin:
            # Si es un socio, elimina los campos 'socio' y 'estado' del formulario, 
            # ya que solo selecciona el cupo y la vista se encarga de la asignación.
            if 'socio' in self.fields:
                del self.fields['socio']
            if 'estado' in self.fields:
                del self.fields['estado']
        else:
            # Si es staff, asegura que la selección de socio sea opcional (puede crear un cupo libre)
            if 'socio' in self.fields:
                self.fields['socio'].required = False