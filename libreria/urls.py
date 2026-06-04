from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
  
urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.index, name='index'),
]