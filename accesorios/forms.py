from django import forms
from .models import ReporteFaltante, Reposicion, Accesorio

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
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
    )
    
    class Meta:
        model = Reposicion
        fields = ['cantidad_comprada']

# ------------------------
# NUEVO: Formulario para ajustar inventario manualmente
class AjusteInventarioForm(forms.ModelForm):
    comentario = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Opcional: explica por qué se ajusta el stock."
    )

    class Meta:
        model = Accesorio
        fields = ['cantidad_total']
        widgets = {
            'cantidad_total': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
