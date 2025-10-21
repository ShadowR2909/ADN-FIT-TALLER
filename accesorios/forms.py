from django import forms
from .models import Accesorio, ReporteFaltante, Reposicion
from proveedores.models import Proveedor

class AccesorioForm(forms.ModelForm):
    class Meta:
        model = Accesorio
        fields = ['nombre', 'cantidad_total', 'descripcion', 'proveedor']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mancuernas 5kg'}),
            'cantidad_total': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proveedor': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'nombre': 'Nombre del Accesorio',
            'cantidad_total': 'Cantidad Inicial',
            'descripcion': 'Descripción (Opcional)',
            'proveedor': 'Proveedor'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)


class ReporteFaltanteForm(forms.ModelForm):
    class Meta:
        model = ReporteFaltante
        fields = ['accesorio', 'cantidad_faltante']
        widgets = {
            'accesorio': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_faltante': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class ReposicionForm(forms.ModelForm):
    cantidad_comprada = forms.IntegerField(
        label="Unidades Compradas (Stock a Añadir)",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Reposicion
        fields = ['cantidad_comprada']
