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
    DESPACHO_CHOICES = [
        ('delivery', 'Delivery'),
        ('en_tienda', 'En Tienda'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Razón Social")
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula o RIF")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    forma_despacho = models.CharField(max_length=20, choices=DESPACHO_CHOICES, default='en_tienda', verbose_name="Forma de Despacho")
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

    MODALIDAD_PAGO_CHOICES = [
        ('un_abono', 'En un solo abono'),
        ('dos_abonos', 'En dos abonos extras'),
    ]

    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('pago_movil', 'Pago Móvil'),
        ('transferencia', 'Transferencia'),
        ('zelle', 'Zelle'),
    ]

    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Entrada")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='entradas', verbose_name="Cliente")
    cliente_presente = models.BooleanField(default=False, verbose_name="¿Cliente está presente?")
    observaciones = models.TextField(verbose_name="Observaciones o Repuestos que lleva")

    abono = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Abono")
    forma_pago_abono = models.CharField(max_length=50, choices=FORMA_PAGO_CHOICES, default='efectivo', verbose_name="Forma de Pago del Abono")
    tasa_dia = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Tasa del Día")
    modalidad_pago_restante = models.CharField(max_length=50, choices=MODALIDAD_PAGO_CHOICES, default='un_abono', verbose_name="Modalidad Pago Restante")

    abono_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Abono Extra")
    forma_pago_abono_extra = models.CharField(max_length=50, choices=FORMA_PAGO_CHOICES, default='efectivo', verbose_name="Forma de Pago del Abono Extra")
    tasa_dia_abono_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Tasa del Día (Abono Extra)")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_taller', verbose_name="Estado")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado por")

    @property
    def total(self):
        # Sumar todos los repuestos y servicios asociados a esta entrada
        total_repuestos = sum(r.valor for r in self.repuestos.all())
        total_servicios = sum(s.valor for s in self.servicios.all())
        return total_repuestos + total_servicios

    @property
    def total_general(self):
        return self.total - self.abono - self.abono_extra

    def __str__(self):
        return f"Entrada {self.id} - {self.cliente.nombre}"

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-fecha']


class Salida(models.Model):
    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('pago_movil', 'Pago Móvil'),
        ('transferencia', 'Transferencia'),
        ('zelle', 'Zelle'),
    ]

    entrada = models.OneToOneField(Entrada, on_delete=models.CASCADE, related_name='salida_rel', verbose_name="Entrada Asociada")
    fecha_entrega = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Entrega")
    pago_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Pago Final Realizado")
    forma_pago_salida = models.CharField(max_length=50, choices=FORMA_PAGO_CHOICES, default='efectivo', verbose_name="Forma de Pago")
    tasa_dia_salida = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Tasa del Día")
    observaciones_entrega = models.TextField(blank=True, verbose_name="Observaciones de Entrega")
    garantia = models.TextField(blank=True, verbose_name="Garantía")
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


class Maquina(models.Model):
    entrada = models.ForeignKey(Entrada, on_delete=models.CASCADE, related_name='maquinas', verbose_name="Entrada Asociada")
    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    serial = models.CharField(max_length=100, blank=True, verbose_name="Serial")

    def __str__(self):
        return f"{self.modelo} (Serial: {self.serial})"

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"

class Repuesto(models.Model):
    entrada = models.ForeignKey(Entrada, on_delete=models.CASCADE, related_name='repuestos', verbose_name="Entrada Asociada")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Repuesto")
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor")

    def __str__(self):
        return f"{self.nombre} (${self.valor})"

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"

class Servicio(models.Model):
    entrada = models.ForeignKey(Entrada, on_delete=models.CASCADE, related_name='servicios', verbose_name="Entrada Asociada")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Servicio")
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor")

    def __str__(self):
        return f"{self.nombre} (${self.valor})"

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
