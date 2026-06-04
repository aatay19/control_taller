from django import forms
from .models import Cliente, Entrada, Salida

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'cedula', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['cliente', 'modelo_maquina', 'observaciones', 'monto_trabajo', 'monto_repuestos', 'abono']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'modelo_maquina': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'monto_trabajo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monto_repuestos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'abono': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = ['entrada', 'pago_final', 'observaciones_entrega']
        widgets = {
            'entrada': forms.Select(attrs={'class': 'form-select', 'readonly': 'readonly'}),
            'pago_final': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones_entrega': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }