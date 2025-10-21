# proveedores/forms.py

from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        # Solo incluimos los 3 atributos esenciales
        fields = ['nombre', 'telefono', 'direccion']
        
        # Opcional: Personalizar widgets (para usar con tu CSS)
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }