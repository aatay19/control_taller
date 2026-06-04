from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('soporte', 'Soporte'),
    ]
 
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Cédula")
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='inventario', verbose_name="Rol")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, verbose_name="Dirección")

    def __str__(self):
        return f"Perfil de {self.user.username}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if not hasattr(instance, 'perfilusuario'):
        PerfilUsuario.objects.create(user=instance)
    else:
        instance.perfilusuario.save()


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    def __str__(self):
        return f"{self.nombre} - {self.cedula}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Entrada(models.Model):
    ESTADO_CHOICES = [
        ('en_taller', 'En Taller'),
        ('entregado', 'Entregado'),
    ]

    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Entrada")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='entradas', verbose_name="Cliente")
    modelo_maquina = models.CharField(max_length=100, verbose_name="Modelo de la Máquina")
    observaciones = models.TextField(verbose_name="Observaciones o Repuestos que lleva")

    monto_trabajo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto del Trabajo")
    monto_repuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto de los Repuestos")
    abono = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Abono")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_taller', verbose_name="Estado")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado por")

    @property
    def total(self):
        return self.monto_trabajo + self.monto_repuestos

    @property
    def total_general(self):
        return self.total - self.abono

    def __str__(self):
        return f"Entrada {self.id} - {self.cliente.nombre} ({self.modelo_maquina})"

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-fecha']


class Salida(models.Model):
    entrada = models.OneToOneField(Entrada, on_delete=models.CASCADE, related_name='salida_rel', verbose_name="Entrada Asociada")
    fecha_entrega = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Entrega")
    pago_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Pago Final Realizado")
    observaciones_entrega = models.TextField(blank=True, verbose_name="Observaciones de Entrega")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Entregado por")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.entrada.estado = 'entregado'
            self.entrada.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salida {self.id} - Entrada {self.entrada.id}"

    class Meta:
        verbose_name = "Salida"
        verbose_name_plural = "Salidas"
        ordering = ['-fecha_entrega']
