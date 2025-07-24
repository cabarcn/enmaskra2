from django.contrib import admin
from .models import UserProfile, Compra, Contenido

# Register your models here.


# Registro del modelo UserProfile con roles incluyendo "administrador"
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'fecha_nacimiento', 'rol', 'is_verified')
    list_filter = ('rol', 'is_verified')
    search_fields = ('user__username', 'rut')

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'contenido', 'monto', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__username', 'contenido__titulo')

@admin.register(Contenido)
class ContenidoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'precio', 'creado_en')
    search_fields = ('titulo', 'usuario__username')
    list_filter = ('tipo', 'creado_en')