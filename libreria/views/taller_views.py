from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from libreria.models import Cliente, Entrada, Salida
from libreria.forms import ClienteForm, EntradaForm, SalidaForm, MaquinaFormSet, RepuestoFormSet, ServicioFormSet
from django.contrib import messages

# --- CLIENTES ---
@login_required
def clientes_lista(request):
    query = request.GET.get('q', '')
    if query:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(cedula__icontains=query)
        )
    else:
        clientes = Cliente.objects.all()
    return render(request, 'clientes/lista.html', {'clientes': clientes, 'query': query})

@login_required
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente registrado correctamente.')
            return redirect('clientes_lista')
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Nuevo Cliente'})

@login_required
def cliente_editar(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('clientes_lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Editar Cliente'})

@login_required
def cliente_eliminar(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado.')
        return redirect('clientes_lista')
    return render(request, 'clientes/eliminar.html', {'cliente': cliente})

@login_required
def api_cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({'success': True, 'id': cliente.id, 'nombre': cliente.nombre, 'cedula': cliente.cedula})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# --- ENTRADAS ---
@login_required
def entradas_lista(request):
    q = request.GET.get('q', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    orden = request.GET.get('orden', '-fecha')

    entradas = Entrada.objects.all()

    if q:
        entradas = entradas.filter(
            Q(cliente__nombre__icontains=q) |
            Q(maquinas__modelo__icontains=q)
        ).distinct()

    if fecha_desde:
        entradas = entradas.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        entradas = entradas.filter(fecha__date__lte=fecha_hasta)

    if orden in ['fecha', '-fecha']:
        entradas = entradas.order_by(orden)

    return render(request, 'entradas/lista.html', {
        'entradas': entradas,
        'q': q,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'orden': orden,
    })

@login_required
def entrada_crear(request):
    if request.method == 'POST':
        form = EntradaForm(request.POST)
        formset = MaquinaFormSet(request.POST)
        repuesto_formset = RepuestoFormSet(request.POST)
        servicio_formset = ServicioFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid() and repuesto_formset.is_valid() and servicio_formset.is_valid():
            entrada = form.save(commit=False)
            entrada.usuario = request.user
            entrada.save()
            
            # Guardar formsets
            for inline_formset in [formset, repuesto_formset, servicio_formset]:
                items = inline_formset.save(commit=False)
                for item in items:
                    item.entrada = entrada
                    item.save()
                for obj in inline_formset.deleted_objects:
                    obj.delete()

            messages.success(request, 'Entrada registrada correctamente.')
            return redirect('entradas_lista')
    else:
        form = EntradaForm()
        formset = MaquinaFormSet()
        repuesto_formset = RepuestoFormSet()
        servicio_formset = ServicioFormSet()
        
    context = {
        'form': form, 
        'formset': formset, 
        'repuesto_formset': repuesto_formset,
        'servicio_formset': servicio_formset,
        'titulo': 'Nueva Entrada'
    }
    return render(request, 'entradas/form.html', context)

@login_required
def entrada_editar(request, id):
    entrada = get_object_or_404(Entrada, id=id)
    if request.method == 'POST':
        form = EntradaForm(request.POST, instance=entrada)
        formset = MaquinaFormSet(request.POST, instance=entrada)
        repuesto_formset = RepuestoFormSet(request.POST, instance=entrada)
        servicio_formset = ServicioFormSet(request.POST, instance=entrada)
        
        if form.is_valid() and formset.is_valid() and repuesto_formset.is_valid() and servicio_formset.is_valid():
            form.save()
            formset.save()
            repuesto_formset.save()
            servicio_formset.save()
            
            messages.success(request, 'Entrada actualizada correctamente.')
            return redirect('entradas_lista')
    else:
        form = EntradaForm(instance=entrada)
        formset = MaquinaFormSet(instance=entrada)
        repuesto_formset = RepuestoFormSet(instance=entrada)
        servicio_formset = ServicioFormSet(instance=entrada)
        
    context = {
        'form': form, 
        'formset': formset, 
        'repuesto_formset': repuesto_formset,
        'servicio_formset': servicio_formset,
        'titulo': 'Editar Entrada'
    }
    return render(request, 'entradas/form.html', context)

@login_required
def entrada_eliminar(request, id):
    entrada = get_object_or_404(Entrada, id=id)
    if request.method == 'POST':
        entrada.delete()
        messages.success(request, 'Entrada eliminada.')
        return redirect('entradas_lista')
    return render(request, 'entradas/eliminar.html', {'entrada': entrada})


# --- TALLER ---
@login_required
def taller_lista(request):
    # Solo las máquinas que están físicamente en el taller
    entradas = Entrada.objects.filter(estado='en_taller')
    return render(request, 'taller/lista.html', {'entradas': entradas})

@login_required
def taller_abono_extra(request, id):
    if request.method == 'POST':
        entrada = get_object_or_404(Entrada, id=id)
        from decimal import Decimal
        import json
        try:
            data = json.loads(request.body)
            abono_extra = Decimal(str(data.get('abono_extra', 0)))
            forma_pago = data.get('forma_pago_abono_extra', 'efectivo')
            tasa_dia = Decimal(str(data.get('tasa_dia_abono_extra', 0)))
            observacion_abono_extra = data.get('observacion_abono_extra', '')
            
            entrada.abono_extra = abono_extra
            entrada.forma_pago_abono_extra = forma_pago
            entrada.tasa_dia_abono_extra = tasa_dia
            entrada.observacion_abono_extra = observacion_abono_extra
            entrada.save()
            
            return JsonResponse({'success': True, 'total_general': entrada.total_general})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


# --- SALIDAS ---
@login_required
def salidas_lista(request):
    q = request.GET.get('q', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    orden = request.GET.get('orden', '-fecha_entrega')

    salidas = Salida.objects.all()

    if q:
        salidas = salidas.filter(
            Q(entrada__cliente__nombre__icontains=q) |
            Q(entrada__maquinas__modelo__icontains=q)
        ).distinct()

    if fecha_desde:
        salidas = salidas.filter(fecha_entrega__date__gte=fecha_desde)
    if fecha_hasta:
        salidas = salidas.filter(fecha_entrega__date__lte=fecha_hasta)

    if orden in ['fecha_entrega', '-fecha_entrega']:
        salidas = salidas.order_by(orden)

    return render(request, 'salidas/lista.html', {
        'salidas': salidas,
        'q': q,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'orden': orden,
    })

@login_required
def salida_crear(request, entrada_id=None):
    entrada_inst = None
    if entrada_id:
        entrada_inst = get_object_or_404(Entrada, id=entrada_id)
        
    if request.method == 'POST':
        form = SalidaForm(request.POST)
        if form.is_valid():
            salida = form.save(commit=False)
            salida.usuario = request.user
            salida.save()
            messages.success(request, 'Salida registrada correctamente.')
            return redirect('salidas_lista')
    else:
        initial = {}
        if entrada_inst:
            initial['entrada'] = entrada_inst
            # Default sugerido para pago final es el monto adeudado
            initial['pago_final'] = entrada_inst.total_general
            
        form = SalidaForm(initial=initial)
        if entrada_inst:
            # Fijar el select para que solo muestre la entrada que se está entregando
            form.fields['entrada'].queryset = Entrada.objects.filter(id=entrada_inst.id)
        else:
            # Solo permitir entradas que no han sido entregadas
            form.fields['entrada'].queryset = Entrada.objects.filter(estado='en_taller')
            
    return render(request, 'salidas/form.html', {'form': form, 'titulo': 'Registrar Salida', 'entrada': entrada_inst})
