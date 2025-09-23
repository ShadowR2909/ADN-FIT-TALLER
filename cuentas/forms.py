from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# Formulario de registro de usuario
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    rol = forms.ChoiceField(
        choices=Profile._meta.get_field('rol').choices, 
        label="Rol de usuario"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "rol"]

    def save(self, commit=True):
        # Guardamos el usuario primero
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

            # Crear perfil automáticamente con el rol seleccionado
            rol = self.cleaned_data['rol']
            Profile.objects.create(user=user, rol=rol)

        return user


# Formulario para editar perfil existente
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["telefono", "rol"]  # agregá otros campos si los tenés
        labels = {
            "telefono": "Teléfono",
            "rol": "Rol",
        }
