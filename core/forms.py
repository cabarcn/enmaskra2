from django import forms
from .models import Contenido
from core.models import ReporteContenido
import bleach

class ContenidoForm(forms.ModelForm):
    class Meta:
        model = Contenido
        fields = ['titulo', 'descripcion', 'tipo', 'archivo', 'precio']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
        }
def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        descripcion_segura = bleach.clean(
            descripcion,
            tags=['b', 'i', 'u', 'strong', 'em', 'br'],  # Permite HTML básico, puedes cambiar a tags=[] si quieres solo texto plano
            attributes={},
            strip=True
        )
        
        return descripcion_segura

class ReporteContenidoForm(forms.ModelForm):
    class Meta:
        model = ReporteContenido
        fields = ['motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el motivo del reporte'
            }),
        }
    