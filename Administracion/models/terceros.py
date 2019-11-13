from datetime import datetime
from django.db import models
from django.db.models import QuerySet

from EVA.General.modelmanagers import ManagerGeneral
from .models import Empresa, TipoIdentificacion, Persona
from .divipol import CentroPoblado
from EVA.General.modeljson import ModelDjangoExtensiones


class TipoTercero(models.Model):
    objects = ManagerGeneral()

    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Tercero'
        verbose_name_plural = 'Tipos de Terceros'

    # Tipos Fijos
    CLIENTE = 1
    PROVEEDOR = 2


class TerceroManger(ManagerGeneral):

    def clientes(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_tercero_id=TipoTercero.CLIENTE)

    def clientes_xa_select(self):
        return self.clientes(True, True)

    def proveedores(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_tercero_id=TipoTercero.PROVEEDOR)

    def proveedores_xa_select(self):
        return self.proveedores(True, True)


class Tercero(models.Model, ModelDjangoExtensiones):
    objects = TerceroManger()

    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False,
                                      unique=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                            verbose_name='Tipo de identificación', null=True, blank=False)
    centro_poblado = models.ForeignKey(CentroPoblado, on_delete=models.DO_NOTHING,
                                       verbose_name='Centro poblado', null=True, blank=False)
    tipo_tercero = models.ForeignKey(TipoTercero, on_delete=models.DO_NOTHING, verbose_name='Tipo Tercero', null=True,
                                     blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tercero'
        verbose_name_plural = 'Terceros'

    @staticmethod
    def from_dictionary(datos: dict) -> 'Tercero':
        """
        Crea una instancia de Tercero con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el tercero.
        :return: Instacia de tercero con la información especificada en el diccionario.
        """
        tercero = Tercero()
        tercero.nombre = datos.get('nombre', '')
        tercero.identificacion = datos.get('identificacion', '')
        tercero.tipo_identificacion_id = datos.get('tipo_identificacion_id', '')
        tercero.estado = datos.get('estado', 'False') == 'True'
        tercero.empresa_id = datos.get('empresa_id', '')
        tercero.fecha_modificacion = datetime.now()
        tercero.tipo_tercero_id = datos.get('tipo_tercero_id', '')
        tercero.centro_poblado_id = datos.get('centro_poblado_id', '')

        return tercero


class UsuarioTercero(Persona):
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=False, blank=False)

    def __str__(self):
        return '{0} {1}'.format(self.usuario.first_name, self.usuario.last_name)

    class Meta:
        verbose_name = 'Usuario Tercero'
        verbose_name_plural = 'Usuarios Terceros'
