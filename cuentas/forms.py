from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from .models import Profile 
from gestion.models import Rutina 

# ----------------------------------------------------------------------
# --- 1. Formulario de Registro Público ---
# Descripción: Utilizado para que nuevos usuarios se registren como 'Socio' por defecto.
# ----------------------------------------------------------------------

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
            
            # Crea el Profile con el rol 'Socio' por defecto
            if not Profile.objects.filter(user=user).exists():
                Profile.objects.create(
                    user=user,
                    telefono=self.cleaned_data.get('telefono', ''),
                    rol='Socio' 
                )
        return user


# ----------------------------------------------------------------------
# --- 2. Formulario para Editar Perfil (User + Profile) ---
# Descripción: Usado por CUALQUIER usuario para editar SU PROPIO perfil.
#              CRÍTICO: Excluye el campo 'rol' para evitar que el usuario lo cambie
#                       y para evitar el error de "obligatorio" al guardar.
# ----------------------------------------------------------------------

class ProfileForm(forms.ModelForm):
    # Campos del modelo User que se editan junto con Profile
    first_name = forms.CharField(max_length=150, required=False, label='Nombre')
    last_name = forms.CharField(max_length=150, required=False, label='Apellido')
    email = forms.EmailField(required=True, label='Correo Electrónico')
    
    class Meta:
        model = Profile
        # 🚨 CORRECCIÓN CRÍTICA: EXCLUIMOS 'rol' para evitar el error de campo obligatorio.
        fields = ["telefono", "fecha_nacimiento"] 
        labels = {
            "telefono": "Teléfono",
            "fecha_nacimiento": "Fecha de Nacimiento"
        }
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        # Eliminamos el pop de 'user' ya que ya no se necesita para la lógica del rol aquí.
        kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # Inicializar campos del modelo User
        if self.instance.pk:
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
            self.initial['email'] = self.instance.user.email
            
        # Aplicar estilo
        for field in self.fields.values():
            if field.widget.__class__ != forms.DateInput: 
                field.widget.attrs.update({'class': 'form-control bg-secondary text-white border-0'})
                
    @transaction.atomic
    def save(self, commit=True):
        # Guardar los datos del Profile (teléfono, fecha_nacimiento)
        profile = super().save(commit=commit)
        
        # Guardar los datos del User (nombre, apellido, email)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        
        if commit:
            user.save()
            
        return profile


# ----------------------------------------------------------------------
# --- 2b. Formulario para Edición de Perfil por el Administrador ---
# Descripción: Usado SOLO en la vista editar_usuario_view para que el Admin
#              pueda cambiar el rol de OTROS usuarios.
# ----------------------------------------------------------------------

class AdminProfileForm(ProfileForm):
    # Hereda todos los campos de ProfileForm (first_name, last_name, email, telefono, fecha_nacimiento)
    
    class Meta(ProfileForm.Meta):
        # AÑADIMOS 'rol' para que el Administrador pueda editarlo
        fields = ProfileForm.Meta.fields + ["rol"] 
        
        # Aseguramos que el label 'rol' se muestre
        labels = ProfileForm.Meta.labels
        labels["rol"] = "Rol de Usuario" 
        
    def __init__(self, *args, **kwargs):
        # Eliminamos 'user' ya que solo se usa para seguridad en ProfileForm
        kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # Aplicar estilo al campo 'rol'
        if 'rol' in self.fields:
             self.fields['rol'].widget.attrs.update({'class': 'form-control bg-secondary text-white border-0'})
             
# ----------------------------------------------------------------------
# --- 3. Formulario de Asignación de Rutinas (Entrenador) ---
# Descripción: Permite al entrenador crear y asignar una rutina.
# ----------------------------------------------------------------------

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
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra el campo 'socio' para mostrar solo a los usuarios con rol 'Socio'
        self.fields['socio'].queryset = User.objects.filter(profile__rol='Socio').order_by('last_name')