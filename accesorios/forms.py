from django import forms
from .models import ReporteFaltante

class ReporteFaltanteForm(forms.ModelForm):
    class Meta:
        model = ReporteFaltante
        fields = ['accesorio', 'cantidad_faltante']
        
        widgets = {
            'accesorio': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_faltante': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }