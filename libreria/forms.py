from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Entrada, Salida, Maquina, Repuesto, Servicio

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'cedula', 'telefono', 'direccion', 'forma_despacho']
        labels = {
            'nombre': 'Razón Social',
            'cedula': 'Cédula o RIF',
            'forma_despacho': 'Forma de Despacho',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'forma_despacho': forms.Select(attrs={'class': 'form-select'}),
        }

class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['cliente', 'cliente_presente', 'observaciones', 'abono']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'cliente_presente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'abono': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

MaquinaFormSet = inlineformset_factory(
    Entrada, 
    Maquina, 
    fields=['modelo', 'serial'], 
    extra=1, 
    can_delete=True,
    widgets={
        'modelo': forms.TextInput(attrs={'class': 'form-control'}),
        'serial': forms.TextInput(attrs={'class': 'form-control'}),
    }
)

RepuestoFormSet = inlineformset_factory(
    Entrada,
    Repuesto,
    fields=['nombre', 'valor'],
    extra=1,
    can_delete=True,
    widgets={
        'nombre': forms.TextInput(attrs={'class': 'form-control repuesto-nombre'}),
        'valor': forms.NumberInput(attrs={'class': 'form-control repuesto-valor', 'step': '0.01'}),
    }
)

ServicioFormSet = inlineformset_factory(
    Entrada,
    Servicio,
    fields=['nombre', 'valor'],
    extra=1,
    can_delete=True,
    widgets={
        'nombre': forms.TextInput(attrs={'class': 'form-control servicio-nombre'}),
        'valor': forms.NumberInput(attrs={'class': 'form-control servicio-valor', 'step': '0.01'}),
    }
)

class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = ['entrada', 'pago_final', 'observaciones_entrega']
        widgets = {
            'entrada': forms.Select(attrs={'class': 'form-select', 'readonly': 'readonly'}),
            'pago_final': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones_entrega': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }