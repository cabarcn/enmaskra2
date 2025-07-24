
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.conf import settings
from cryptography.fernet import Fernet
from django.conf import settings



class UserProfile(models.Model):
    ROLES = [
        ('creador', 'Creador de contenido'),
        ('suscriptor', 'Suscriptor'),
        ('administrador', 'Administrador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    _rut = models.BinaryField(null=True, blank=True, editable=False)
    _fecha_nacimiento = models.BinaryField(null=True, blank=True, editable=False)
    _correo = models.BinaryField(null=True, blank=True, editable=False)

    is_verified = models.BooleanField(default=False)
    rol = models.CharField(max_length=20, choices=ROLES, default='suscriptor')

    @property
    def rut(self):
        if self._rut:
            return Fernet(settings.FERNET_KEY).decrypt(self._rut).decode()
        return None

    @rut.setter
    def rut(self, value):
        self._rut = Fernet(settings.FERNET_KEY).encrypt(value.encode())

    @property
    def fecha_nacimiento(self):
        if self._fecha_nacimiento:
            return Fernet(settings.FERNET_KEY).decrypt(self._fecha_nacimiento).decode()
        return None

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, value):
        self._fecha_nacimiento = Fernet(settings.FERNET_KEY).encrypt(str(value).encode())

    @property
    def correo(self):
        if self._correo:
            return Fernet(settings.FERNET_KEY).decrypt(self._correo).decode()
        return None

    @correo.setter
    def correo(self, value):
        self._correo = Fernet(settings.FERNET_KEY).encrypt(value.encode())

    def calcular_edad(self):
        if self.fecha_nacimiento:
            fecha = date.fromisoformat(self.fecha_nacimiento)
            hoy = date.today()
            edad = hoy.year - fecha.year - (
                (hoy.month, hoy.day) < (fecha.month, fecha.day)
            )
            return edad
        return None

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Contenido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=10, choices=[('imagen', 'Imagen'), ('video', 'Video')])
    archivo = models.FileField(upload_to='contenido/')
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.archivo.name}"


class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado')], default='pagado')

    def __str__(self):
        return f"{self.usuario.username} compró {self.contenido.titulo} - ${self.monto}"

class ReporteContenido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('resuelto', 'Resuelto'),
    ]

    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    decision = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reporte de {self.contenido.titulo} por {self.usuario.username}"