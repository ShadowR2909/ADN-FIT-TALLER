from django import forms
from django.contrib.auth.models import User
from .models import Plan, Membresia, Clase, Rutina 

# --- 1. Formulario para Planes de Membresía (Admin) ---

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['nombre', 'precio', 'duracion_dias', 'descripcion']
        labels = {
            'nombre': 'Nombre del Plan',
            'precio': 'Precio ($)',
            'duracion_dias': 'Duración (días)',
            'descripcion': 'Descripción y Beneficios',
        }
        widgets = {
            'nombre': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duracion_dias': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --- 2. Formulario para Asignar/Editar Membresías (Admin) ---

class MembresiaForm(forms.ModelForm):
    socio_user = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__rol='Socio').order_by('last_name'),
        label="Socio a Asignar/Actualizar",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Membresia
        fields = ['plan', 'fecha_vencimiento', 'activo']
        labels = {
            'plan': 'Plan Seleccionado',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'activo': 'Activa',
        }
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            kwargs.setdefault('initial', {})['socio_user'] = instance.socio
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        socio_user = self.cleaned_data.pop('socio_user')
        membresia = super().save(commit=False)
        membresia.socio = socio_user
        if commit:
            membresia.save()
        return membresia

# --- 3. Formulario para Clases (Admin) ---

class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = ['nombre', 'dia_semana', 'hora_inicio', 'entrenador', 'capacidad']
        labels = {
            'dia_semana': 'Día de la Semana',
            'hora_inicio': 'Hora de Inicio',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            # El campo 'entrenador' ya se filtra automáticamente gracias a limit_choices_to en models.py
            'entrenador': forms.Select(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
# --- 4. Formulario para Rutinas (Entrenador) ---

class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = ['socio', 'nombre', 'descripcion', 'activa']
        
        widgets = {
            # Filtro de socio en views para asegurar el rol 'Socio'
            'socio': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aseguramos que solo se puedan seleccionar Socios
        self.fields['socio'].queryset = User.objects.filter(profile__rol='Socio').order_by('last_name')
        self.fields['socio'].label = 'Asignar a Socio'