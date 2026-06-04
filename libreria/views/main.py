from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from libreria.models import Entrada, Salida

@login_required
def index(request):
    maquinas_en_taller = Entrada.objects.filter(estado='en_taller').count()
    maquinas_entregadas = Salida.objects.count()
    
    ultimas_ingresadas = Entrada.objects.select_related('cliente').order_by('-fecha')[:5]
    ultimas_entregadas = Salida.objects.select_related('entrada', 'entrada__cliente').order_by('-fecha_entrega')[:5]
    
    context = {
        'maquinas_en_taller': maquinas_en_taller,
        'maquinas_entregadas': maquinas_entregadas,
        'ultimas_ingresadas': ultimas_ingresadas,
        'ultimas_entregadas': ultimas_entregadas,
    }
    return render(request, 'index.html', context)

