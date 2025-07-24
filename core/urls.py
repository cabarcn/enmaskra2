"""enmaskra2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from core.views import CustomLoginView
from django.shortcuts import redirect
from django.views.generic import TemplateView
from core.views import reportar_contenido
from core.views import admin_reportes
from .views import galeria_modelos

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('contacto/', views.contacto, name='contacto'),
    path('registro/', views.registro, name='registro'),
    #path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('login/', CustomLoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('subir/', views.subir_contenido, name='subir_contenido'),
    path('contenido-editar/<int:contenido_id>/', views.editar_contenido, name='editar_contenido'),
    path('mis-contenidos/', views.mis_contenidos, name='mis_contenidos'),
    path('contenido/<int:contenido_id>/eliminar/', views.eliminar_contenido, name='eliminar_contenido'),
    path('contenido/<int:contenido_id>/', views.detalle_contenido, name='detalle_contenido'),
    path('comprar/<int:contenido_id>/', views.comprar_contenido, name='comprar_contenido'),
    path('comprar/<int:contenido_id>/', views.procesar_compra, name='procesar_compra'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
    path('panel-administracion/', views.admin_panel, name='admin_panel'),
    path('admin-panel/usuario/<int:pk>/toggle/', views.toggle_usuario, name='toggle_usuario'),
    path('admin-panel/contenido/<int:pk>/toggle/', views.toggle_contenido, name='toggle_contenido'),
    path('admin/toggle_usuario/<int:user_id>/', views.toggle_usuario, name='toggle_usuario'),
    path('admin/toggle_contenido/<int:contenido_id>/', views.toggle_contenido, name='toggle_contenido'),
    path('panel/editar_usuario/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('privacidad/', TemplateView.as_view(template_name='core/privacidad.html'), name='privacidad'),
    path('terminos/', TemplateView.as_view(template_name='core/terminos.html'), name='terminos'),
    path('reportar/<int:contenido_id>/', reportar_contenido, name='reportar_contenido'),
    path('panel/reportes/resolver/<int:reporte_id>/', views.resolver_reporte, name='resolver_reporte'),
    path('panel/reportes/', views.admin_reportes, name='admin_reportes'),
    path("galeria-modelos/", galeria_modelos, name="galeria_modelos"),
    path('galeria/ajax/', views.cargar_mas_fotos, name='cargar_mas_fotos'),

    






    
]
