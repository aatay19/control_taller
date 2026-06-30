from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
  
urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.index, name='index'),

    path('clientes/', views.clientes_lista, name='clientes_lista'),
    path('clientes/crear/', views.cliente_crear, name='cliente_crear'),
    path('clientes/editar/<int:id>/', views.cliente_editar, name='cliente_editar'),
    path('clientes/eliminar/<int:id>/', views.cliente_eliminar, name='cliente_eliminar'),
    path('api/clientes/crear/', views.api_cliente_crear, name='api_cliente_crear'),
    
    path('entradas/', views.entradas_lista, name='entradas_lista'),
    path('entradas/crear/', views.entrada_crear, name='entrada_crear'),
    path('entradas/editar/<int:id>/', views.entrada_editar, name='entrada_editar'),
    path('entradas/eliminar/<int:id>/', views.entrada_eliminar, name='entrada_eliminar'),
    path('entradas/<int:id>/detalle/', views.entrada_detalle_json, name='entrada_detalle'),
    path('entradas/<int:id>/pdf/', views.entrada_pdf, name='entrada_pdf'),
    
    path('taller/', views.taller_lista, name='taller_lista'),
    path('taller/abono_extra/<int:id>/', views.taller_abono_extra, name='taller_abono_extra'),
    
    path('salidas/', views.salidas_lista, name='salidas_lista'),
    path('salidas/crear/', views.salida_crear, name='salida_crear'),
    path('salidas/crear/<int:entrada_id>/', views.salida_crear, name='salida_crear_con_entrada'),
    path('salidas/<int:id>/pdf/', views.salida_pdf, name='salida_pdf'),
]
