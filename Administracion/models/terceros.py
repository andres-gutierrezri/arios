from django.db import models
from .models import Empresa, TipoIdentificacion, Persona
from .divipol import CentroPoblado


class TipoTercero(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Tercero'
        verbose_name_plural = 'Tipos de Terceros'


class Tercero(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False,
                                      unique=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    terceros = models.CharField(max_length=100, verbose_name='Tipo', null=False, blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                            verbose_name='Tipo de identificación', null=True, blank=False)
    centro_poblado = models.ForeignKey(CentroPoblado, on_delete=models.DO_NOTHING,
                                       verbose_name='Centro poblado', null=True, blank=False)
    tipo_tercero = models.ForeignKey(TipoTercero, on_delete=models.DO_NOTHING, verbose_name='Tipo tercero', null=True,
                                     blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tercero'
        verbose_name_plural = 'Terceros'


class UsuarioTercero(Persona):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    apellido = models.CharField(max_length=100, verbose_name='Apellido', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=False, blank=False)

    def __str__(self):
        return '{0} {1}'.format(self.nombre, self.apellido)

    class Meta:
        verbose_name = 'Usuario Tercero'
        verbose_name_plural = 'Usuarios Terceros'
