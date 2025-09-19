from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from .models import Profile

class RegistroUsuarioForm(UserCreationForm):
    # ... (otros campos)

    email = forms.EmailField(label='Correo Electrónico', required=True)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), label="Grupo")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password', 'password2', 'grupo']
        labels = {
            'username': 'Nombre de Usuario',
            'password2': 'Confirmar Contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cambiar el texto de ayuda y los errores de la contraseña
        self.fields['password2'].help_text = 'Confirma tu contraseña. Debe ser la misma que la anterior.'
        self.fields['password'].help_text = '''
            <ul>
                <li>Tu contraseña no puede ser demasiado similar a tu otra información personal.</li>
                <li>Tu contraseña debe contener al menos 8 caracteres.</li>
                <li>Tu contraseña no puede ser una contraseña comúnmente usada.</li>
                <li>Tu contraseña no puede ser completamente numérica.</li>
            </ul>
        '''
        self.fields['password'].error_messages['too_similar'] = 'Tu contraseña es demasiado similar a tu otra información personal.'
        # y así para los demás errores..

        
def ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('telefono', 'rol')  # otros campos del perfil si los hay