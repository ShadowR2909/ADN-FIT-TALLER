# cuentas/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from .models import Profile 
from gestion.models import Rutina # Importación actualizada

# --- 1. Formulario de Registro Público ---

class RegistroUsuarioForm(UserCreationForm):
    # Campos adicionales para el modelo User
    email = forms.EmailField(required=True, label="Correo Electrónico")
    telefono = forms.CharField(max_length=30, required=False, label="Teléfono de Contacto")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',) 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilo Bootstrap
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control bg-secondary text-white border-0'})
            
    @transaction.atomic
    def save(self, commit=True):
        """Crea el User y el Profile con rol 'Socio'."""
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Verifica que no exista un perfil para este usuario antes de crear
            if not Profile.objects.filter(user=user).exists():
                Profile.objects.create(
                    user=user,
                    telefono=self.cleaned_data.get('telefono', ''),
                    rol='Socio' 
                )
        return user


# --- 2. Formulario para Editar Perfil (User + Profile) ---

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, label='Nombre')
    last_name = forms.CharField(max_length=150, required=False, label='Apellido')
    email = forms.EmailField(required=True, label='Correo Electrónico')
    
    class Meta:
        model = Profile
        fields = ["telefono", "rol", "fecha_nacimiento"] 
        labels = {
            "telefono": "Teléfono",
            "rol": "Rol",
            "fecha_nacimiento": "Fecha de Nacimiento"
        }
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
            self.initial['email'] = self.instance.user.email
        
        for field in self.fields.values():
            # Aplica el estilo a la mayoría de los campos
            if field.widget.__class__ != forms.DateInput: # Evita cambiar el type='date'
                field.widget.attrs.update({'class': 'form-control bg-secondary text-white border-0'})
            
    @transaction.atomic
    def save(self, commit=True):
        profile = super().save(commit=commit)
        
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        
        if commit:
            user.save()
            
        return profile

# --- 3. Formulario de Asignación de Rutinas (Entrenador) ---

class RutinaForm(forms.ModelForm):
    """
    Formulario para que el Entrenador asigne una rutina a un Socio.
    """
    class Meta:
        model = Rutina
        fields = ['socio', 'nombre', 'descripcion', 'activa']
        labels = {
            'socio': 'Asignar a Socio',
            'nombre': 'Título de la Rutina',
            'descripcion': 'Contenido del Plan de Entrenamiento',
            'activa': '¿Activar Rutina?',
        }
        
        widgets = {
            'socio': forms.Select(attrs={'class': 'form-control bg-secondary text-white border-0'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control bg-secondary text-white border-0', 'placeholder': 'Ej: Fuerza Nivel I'}),
            'descripcion': forms.Textarea(attrs={'rows': 5, 'class': 'form-control bg-secondary text-white border-0', 'placeholder': 'Detalles de ejercicios, series y repeticiones...'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Checkbox no usa el mismo estilo de control
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra el campo 'socio' para mostrar solo a los usuarios con rol 'Socio'
        # Usamos el related_name 'profile' (Profile.user) para un filtro eficiente.
        self.fields['socio'].queryset = User.objects.filter(profile__rol='Socio').order_by('last_name')
