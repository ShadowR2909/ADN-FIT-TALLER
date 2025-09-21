from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Profile


# ---------- Registro de Usuario ----------
class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    email = forms.EmailField(label='Correo Electrónico', required=True)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), label="Grupo")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'grupo']
        labels = {
            'username': 'Nombre de Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar los textos de ayuda de contraseña
        self.fields['password2'].help_text = 'Confirma tu contraseña. Debe ser la misma que la anterior.'
        self.fields['password1'].help_text = '''
            <ul>
                <li>Tu contraseña no puede ser demasiado similar a tu otra información personal.</li>
                <li>Tu contraseña debe contener al menos 8 caracteres.</li>
                <li>Tu contraseña no puede ser una contraseña comúnmente usada.</li>
                <li>Tu contraseña no puede ser completamente numérica.</li>
            </ul>
        '''
        self.fields['password1'].error_messages['too_similar'] = 'Tu contraseña es demasiado similar a tu otra información personal.'
        # Puedes seguir agregando mensajes personalizados aquí


# ---------- Edición de Perfil ----------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('telefono', 'rol')  # agregar más campos de Profile si existen
