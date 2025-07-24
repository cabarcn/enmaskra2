from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ContenidoForm
from datetime import datetime, date
from .models import UserProfile
from itertools import cycle
from .forms import ContenidoForm
from .models import Contenido, Compra
from django.http import HttpResponseForbidden
from django.db import IntegrityError
from django.contrib.auth.views import LoginView
import logging
from core.forms import ReporteContenidoForm
from django.contrib.auth.decorators import user_passes_test
from core.models import ReporteContenido
import requests
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger('core.security')

class CustomLoginView(LoginView):

    def form_invalid(self, form):
        ip = self.request.META.get('REMOTE_ADDR')
        username = self.request.POST.get('username')
        logger.warning(f"Intento de login fallido - Usuario: {username} - IP: {ip}")
        messages.error(self.request, "Credenciales inválidas. Por favor verifica tus datos.")
        return super().form_invalid(form)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# Create your views here.
def index(request):
    return redirect('login')

#def login(request):
 #   return render(request, 'core/login.html')


@login_required
def home(request):
    perfil = request.user.userprofile
    if not perfil.is_verified:
        messages.warning(request, "Debes verificar tu edad para acceder.")
        return redirect('verificar_datos')
    
    contenidos = Contenido.objects.all().order_by('-creado_en')
    
    comprados = []
    if request.user.is_authenticated:
         comprados = list(Compra.objects.filter(usuario=request.user, estado='pagado').values_list('contenido_id', flat=True))
        
    modelos =[
        { 'nombre': 'Camila', 'descripcion': 'Modelo fitness', 'imagen': 'core/img/modelo_mujer.jpg'},
        {'nombre': 'Daniel', 'descripcion': 'Bailarín exótico', 'imagen': 'core/img/modelo_hombre.png'},
    ] 
    
    return render(request, 'core/home.html', {
        'contenidos': contenidos,
        'modelos' : modelos,
        'comprados': comprados})

def contacto(request):
    return render(request, 'core/contacto.html')

def validar_rut(rut):
    rut = rut.upper().replace("-", "").replace(".", "")
    aux = rut[:-1]
    dv = rut[-1:]
    try:
        revertido = map(int, reversed(str(aux)))
        factores = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(revertido, factores))
        res = (-s) % 11
        dv_calc = "K" if res == 10 else str(res)
        return dv == dv_calc
    except:
        return False
    
def rut_ya_existe(rut_a_verificar):
    for perfil in UserProfile.objects.all():
        if perfil.rut == rut_a_verificar:
            return True
    return False

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')
        rol = request.POST.get('rol')
        rut = request.POST.get('rut')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        if not all([username, email, password1, password2, rol, rut, fecha_nacimiento]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('registro')
        
        if rol not in ['creador', 'suscriptor']:
            messages.error(request, "Debes seleccionar un tipo de cuenta.")
            return redirect('registro')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request,'core/registro.html', request.POST)
            #return redirect('registro')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('registro')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect('registro')

        #if UserProfile.objects.filter(rut=rut).exists():
        if rut_ya_existe(rut):
            messages.error(request, "El RUT ya está registrado.")
            return redirect('registro')

        if not validar_rut(rut):
            messages.error(request, "El RUT ingresado no es válido.")
            return redirect('registro')

        try:
            fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Fecha de nacimiento inválida.")
            return redirect('registro')

        edad = (date.today() - fecha_nac).days // 365
        if edad < 18:
            messages.error(request, "Debes tener al menos 18 años para registrarte.")
            return redirect('registro')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            UserProfile.objects.create(user=user, rol=rol, rut=rut, fecha_nacimiento=fecha_nac,is_verified=True)

            login(request, user)
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect('login')
        except IntegrityError as e:
            logger.warning(f"Error al registrar usuario {username} desde IP {get_client_ip(request)}: {str(e)}")
            messages.error(request, "Error al registrar. Intenta nuevamente.")
            return redirect('registro')

    return render(request, 'core/registro.html')

@login_required
def verificar_datos(request):
    perfil = request.user.userprofile
    if request.method == 'POST':
        rut = request.POST.get('rut')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        if not validar_rut(rut):
            messages.error(request, "El RUT ingresado no es válido.")
            return redirect('verificar_datos')

        try:
            fecha_nac_obj = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Fecha de nacimiento inválida.")
            return redirect('verificar_datos')

        edad = (date.today() - fecha_nac_obj).days // 365
        if edad < 18:
            messages.error(request, "Debes tener al menos 18 años.")
            return redirect('verificar_datos')

        perfil.rut = rut
        perfil.fecha_nacimiento = fecha_nac_obj
        perfil.is_verified = True
        perfil.save()
        messages.success(request, "Verificación completada correctamente.")
        return redirect('home')

    return render(request, 'core/verificar_datos.html', {'perfil': perfil})


@login_required
def subir_contenido(request):
    perfil = request.user.userprofile
    if perfil.rol != 'creador':
        return HttpResponseForbidden("Solo los creadores de contenido pueden subir archivos.")    
    
    if request.method == 'POST':
        form = ContenidoForm(request.POST, request.FILES)
        if form.is_valid():
            contenido = form.save(commit=False)
            contenido.usuario = request.user
            contenido.save()
            messages.success(request, "Contenido subido correctamente.")
            return redirect('mis_contenidos')
        else:
            messages.error(request, "Error al subir contenido. Revisa los campos.")
    else:
        form = ContenidoForm()
    return render(request, 'core/subir_contenido.html', {'form': form})


@login_required
def editar_contenido(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id, usuario=request.user)

    if request.method == 'POST':
        form = ContenidoForm(request.POST, request.FILES, instance=contenido)
        if form.is_valid():
            form.save()
            messages.success(request, "Contenido actualizado correctamente.")
            return redirect('mis_contenidos')  # O a una vista personalizada como 'mis_contenidos'
        else:
            messages.error(request, "❌ Por favor corrige los errores en el formulario.")
    else:
        form = ContenidoForm(instance=contenido)

    return render(request, 'core/editar_contenido.html', {'form': form, 'contenido': contenido})

@login_required
def mis_contenidos(request):
    contenidos = Contenido.objects.filter(usuario=request.user).order_by('-creado_en')
    return render(request, 'core/mis_contenidos.html', {'contenidos': contenidos})

@login_required
def eliminar_contenido(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id)

    # Solo el usuario que lo subió puede eliminarlo
    if contenido.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar este contenido.")
        return redirect('mis_contenidos')  # O a donde consideres más apropiado

    contenido.delete()
    messages.success(request, "Contenido eliminado correctamente.")
    return redirect('mis_contenidos')

@login_required
def detalle_contenido(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id)
    ya_comprado = Compra.objects.filter(usuario=request.user, contenido=contenido, estado='pagado').exists()

    return render(request, 'core/detalle_contenido.html', {
        'contenido': contenido,
        'ya_comprado': ya_comprado
    })
    
@login_required
def comprar_contenido(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id)

    # Evitar duplicados
    ya_comprado = Compra.objects.filter(usuario=request.user, contenido=contenido, estado='pagado').exists()
    if ya_comprado:
        messages.info(request, "Ya has comprado este contenido.")
        return redirect('detalle_contenido', contenido_id=contenido_id)

    # Simular pago exitoso (esto será reemplazado por pasarela real luego)
    Compra.objects.create(
        usuario=request.user,
        contenido=contenido,
        monto=contenido.precio,
        estado='pagado'
    )
    messages.success(request, "✅ ¡Compra realizada con éxito!")
    return redirect('detalle_contenido', contenido_id=contenido_id)

@login_required
def procesar_compra(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id)

    # Verificar si ya fue comprado
    ya_comprado = Compra.objects.filter(usuario=request.user, contenido=contenido, estado='pagado').exists()
    if ya_comprado:
        messages.info(request, "Ya has comprado este contenido.")
        return redirect('detalle_contenido', contenido_id=contenido.id)
    
    # Aquí iría la lógica real de pasarela de pago (Stripe, PayPal, etc.)
    # En este ejemplo asumimos pago exitoso

    # Simulación de pago exitoso (reemplazar con integración real a futuro)
    compra = Compra.objects.create(
        usuario=request.user,
        contenido=contenido,
        monto=contenido.precio,
        estado='pagado',   # en un caso real podrías validar respuesta de la API
        fecha=datetime.now()
    )

    messages.success(request, f"Compra realizada con éxito. Has adquirido '{contenido.titulo}'.")
    return redirect('detalle_contenido', contenido_id=contenido.id)

@login_required
def mis_compras(request):
    compras = Compra.objects.filter(usuario=request.user, estado='pagado').select_related('contenido').order_by('-fecha')
    return render(request, 'core/mis_compras.html', {'compras': compras})


@login_required
def admin_panel(request):
    perfil = request.user.userprofile
    if perfil.rol != 'administrador':
        messages.error(request, "No tienes permisos para acceder al panel de administración.")
        return redirect('home')

    perfiles = UserProfile.objects.select_related('user').all()
    contenidos = Contenido.objects.select_related('usuario').all()
    compras = Compra.objects.select_related('usuario', 'contenido').order_by('-fecha')

    return render(request, 'core/admin_panel.html', {
        'perfiles': perfiles,
        'contenidos': contenidos,
        'compras': compras
    })
    
@login_required
def toggle_usuario(request, pk):
    perfil = request.user.userprofile
    if perfil.rol != 'administrador':
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('home')

    try:
        user_profile = UserProfile.objects.get(pk=pk)
        user_profile.user.is_active = not user_profile.user.is_active
        user_profile.user.save()
        estado = "activado" if user_profile.user.is_active else "suspendido"
        messages.success(request, f"Usuario {user_profile.user.username} {estado} correctamente.")
    except UserProfile.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")

    return redirect('admin_panel')


@login_required
def toggle_contenido(request, pk):
    perfil = request.user.userprofile
    if perfil.rol != 'administrador':
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('home')

    try:
        contenido = Contenido.objects.get(pk=pk)
        contenido.visible = not contenido.visible
        contenido.save()
        estado = "visible" if contenido.visible else "oculto"
        messages.success(request, f"Contenido '{contenido.titulo}' ahora está {estado}.")
    except Contenido.DoesNotExist:
        messages.error(request, "Contenido no encontrado.")

    return redirect('admin_panel')

def es_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.rol == 'administrador'

@login_required
@user_passes_test(es_admin)
def toggle_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    # Evitar que el admin suspenda a sí mismo o a superusuarios
    if usuario == request.user or usuario.is_superuser:
        messages.warning(request, "No puedes modificar este usuario.")
        return redirect('admin_panel')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = "activado" if usuario.is_active else "suspendido"
    messages.success(request, f"El usuario {usuario.username} ha sido {estado}.")
    return redirect('admin_panel')

def es_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.rol == 'administrador'

@login_required
@user_passes_test(es_admin)
def toggle_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    # Evitar que el admin suspenda a sí mismo o a superusuarios
    if usuario == request.user or usuario.is_superuser:
        messages.warning(request, "No puedes modificar este usuario.")
        return redirect('admin_panel')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = "activado" if usuario.is_active else "suspendido"
    messages.success(request, f"El usuario {usuario.username} ha sido {estado}.")
    return redirect('admin_panel')

@login_required
@user_passes_test(es_admin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    perfil = get_object_or_404(UserProfile, user=usuario)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        rol = request.POST.get('rol')
        is_verified = request.POST.get('is_verified') == 'on'

        if username and email and rol:
            usuario.username = username
            usuario.email = email
            usuario.save()

            perfil.rol = rol
            perfil.is_verified = is_verified
            perfil.save()

            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('admin_panel')
        else:
            messages.error(request, "Todos los campos son obligatorios.")

    context = {
        'usuario': usuario,
        'perfil': perfil
    }
    return render(request, 'core/editar_usuario.html', context)

@login_required
def reportar_contenido(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id)
    
    if request.method == 'POST':
        form = ReporteContenidoForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario = request.user
            reporte.contenido = contenido
            reporte.save()
            messages.success(request, 'Reporte enviado correctamente.')
            return redirect('home')
    else:
        form = ReporteContenidoForm()

    return render(request, 'core/reportar_contenido.html', {'form': form, 'contenido': contenido})

def es_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.rol == 'administrador'

@user_passes_test(es_admin)
def admin_reportes(request):
    reportes = ReporteContenido.objects.all().order_by('-fecha')
    return render(request, 'core/admin_reportes.html', {'reportes': reportes})

def resolver_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteContenido, id=reporte_id)

    if request.method == 'POST':
        decision = request.POST.get('decision')
        reporte.decision = decision
        reporte.estado = 'resuelto'
        reporte.save()
        messages.success(request, 'Reporte resuelto correctamente.')
        return redirect('admin_reportes')

    return render(request, 'core/resolver_reporte.html', {'reporte': reporte})

def privacidad(request):
    return render(request, 'core/privacidad.html')

def terminos(request):
    return render(request, 'core/terminos.html')

def galeria_modelos(request):
    headers = {
        "Authorization": settings.PEXELS_API_KEY
    }
    params = {
        "query": "modelo",  # Puedes cambiarlo por "fashion", "beauty", etc.
        "per_page": 9
    }
    response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    
    print("Estado:", response.status_code)
    print("Respuesta:", response.text)  # <-- Agregado para depuración
    
    data = response.json()
    fotos = data.get("photos", [])

    return render(request, "core/galeria_modelos.html", {"fotos": fotos})

def cargar_mas_fotos(request):
    page = int(request.GET.get('page', 1))
    headers = {
        "Authorization": settings.PEXELS_API_KEY
    }
    params = {
        "query": "models",  # puedes hacer dinámico esto
        "per_page": 9,
        "page": page
    }
    response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse({"photos": data["photos"]})
    else:
        return JsonResponse({"error": "No se pudo cargar más fotos."}, status=400)


