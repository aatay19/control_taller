from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from libreria.models import Cliente, Entrada, Salida
from libreria.forms import ClienteForm, EntradaForm, SalidaForm
from django.contrib import messages

# --- CLIENTES ---
@login_required
def clientes_lista(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista.html', {'clientes': clientes})

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


# --- ENTRADAS ---
@login_required
def entradas_lista(request):
    entradas = Entrada.objects.all()
    return render(request, 'entradas/lista.html', {'entradas': entradas})

@login_required
def entrada_crear(request):
    if request.method == 'POST':
        form = EntradaForm(request.POST)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.usuario = request.user
            entrada.save()
            messages.success(request, 'Entrada registrada correctamente.')
            return redirect('entradas_lista')
    else:
        form = EntradaForm()
    return render(request, 'entradas/form.html', {'form': form, 'titulo': 'Nueva Entrada'})

@login_required
def entrada_editar(request, id):
    entrada = get_object_or_404(Entrada, id=id)
    if request.method == 'POST':
        form = EntradaForm(request.POST, instance=entrada)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada actualizada correctamente.')
            return redirect('entradas_lista')
    else:
        form = EntradaForm(instance=entrada)
    return render(request, 'entradas/form.html', {'form': form, 'titulo': 'Editar Entrada'})

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


# --- SALIDAS ---
@login_required
def salidas_lista(request):
    salidas = Salida.objects.all()
    return render(request, 'salidas/lista.html', {'salidas': salidas})

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
