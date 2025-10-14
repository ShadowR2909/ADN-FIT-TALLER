from django import forms
from .models import ReporteFaltante, Reposicion

class ReporteFaltanteForm(forms.ModelForm):
    class Meta:
        model = ReporteFaltante
        fields = ['accesorio', 'cantidad_faltante']
        
        widgets = {
            'accesorio': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_faltante': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class ReposicionForm(forms.ModelForm):
    # Sobrescribimos el campo para usarlo en la vista, aunque Reposicion es un modelo.
    # Podríamos usar un Simple Form, pero usar ModelForm es más simple aquí.
    cantidad_comprada = forms.IntegerField(
        label="Unidades Compradas (Stock a Añadir)",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
    )
    
    class Meta:
        model = Reposicion
        fields = ['cantidad_comprada']