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
        fields = ['cliente', 'cliente_presente', 'observaciones', 'observacion_pago', 'abono', 'fecha_abono_inicial', 'forma_pago_abono', 'tasa_dia', 'modalidad_pago_restante']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'cliente_presente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacion_pago': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej. Referencia de transferencia...'}),
            'abono': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_abono_inicial': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'forma_pago_abono': forms.Select(attrs={'class': 'form-select'}),
            'tasa_dia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'modalidad_pago_restante': forms.Select(attrs={'class': 'form-select'}),
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
    fields=['nombre', 'cantidad', 'valor'],
    extra=1,
    can_delete=True,
    widgets={
        'nombre': forms.TextInput(attrs={'class': 'form-control repuesto-nombre'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control repuesto-cantidad', 'min': '1'}),
        'valor': forms.NumberInput(attrs={'class': 'form-control repuesto-valor', 'step': '0.01'}),
    }
)

ServicioFormSet = inlineformset_factory(
    Entrada,
    Servicio,
    fields=['nombre', 'cantidad', 'valor'],
    extra=1,
    can_delete=True,
    widgets={
        'nombre': forms.TextInput(attrs={'class': 'form-control servicio-nombre'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control servicio-cantidad', 'min': '1'}),
        'valor': forms.NumberInput(attrs={'class': 'form-control servicio-valor', 'step': '0.01'}),
    }
)

class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = ['entrada', 'fecha_entrega', 'pago_final', 'forma_pago_salida', 'tasa_dia_salida', 'observacion_pago_final', 'observaciones_entrega', 'garantia']
        widgets = {
            'entrada': forms.Select(attrs={'class': 'form-select', 'readonly': 'readonly'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pago_final': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pago_salida': forms.Select(attrs={'class': 'form-select'}),
            'tasa_dia_salida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacion_pago_final': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej. Referencia de transferencia...'}),
            'observaciones_entrega': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'garantia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej: 30 días de garantía por el servicio realizado...'}),
        }