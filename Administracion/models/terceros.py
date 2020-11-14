from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet

from EVA.General.modelmanagers import ManagerGeneral
from .models import Empresa, TipoIdentificacion, Persona
from .divipol import CentroPoblado, Municipio
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
    SUPERVISOR = 3
    INTERVENTOR = 4


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

    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=True, blank=False)
    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False,
                                      unique=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                            verbose_name='Tipo de identificación', null=True, blank=False)
    ciudad = models.ForeignKey(Municipio, on_delete=models.DO_NOTHING, verbose_name='Ciudad', null=True, blank=True,
                               related_name='proveedor_ciudad')
    centro_poblado = models.ForeignKey(CentroPoblado, on_delete=models.DO_NOTHING,
                                       verbose_name='Centro poblado', null=True, blank=False)
    tipo_tercero = models.ForeignKey(TipoTercero, on_delete=models.DO_NOTHING, verbose_name='Tipo Tercero', null=True,
                                     blank=False)
    direccion = models.CharField(max_length=100, verbose_name='Dirección', null=True, blank=False)
    telefono = models.CharField(max_length=30, verbose_name='Teléfono', null=True, blank=False)
    fax = models.CharField(max_length=30, verbose_name='fax', null=True, blank=True)
    telefono_fijo_principal = models.CharField(max_length=30, verbose_name='Teléfono Fijo Principal',
                                               null=True, blank=True)
    telefono_fijo_auxiliar = models.CharField(max_length=30, verbose_name='Teléfono Fijo auxiliar',
                                              null=True, blank=True)
    telefono_movil_principal = models.CharField(max_length=30, verbose_name='Teléfono Movil Principal',
                                                null=True, blank=True)
    telefono_movil_auxiliar = models.CharField(max_length=30, verbose_name='Teléfono Movil Auxiliar',
                                               null=True, blank=True)
    correo_principal = models.CharField(max_length=30, verbose_name='Correo Principal', null=True, blank=True)
    correo_auxiliar = models.CharField(max_length=30, verbose_name='Correo Auxiliar', null=True, blank=True)
    nombre_rl = models.CharField(max_length=100, verbose_name='Nombre del Representante Legal', null=True, blank=True)
    identificacion_rl = models.CharField(max_length=100, verbose_name='Identificación del Representante Legal',
                                         null=True, blank=True)
    lugar_expedicion_rl = models.ForeignKey(Municipio, on_delete=models.DO_NOTHING, null=True, blank=True,
                                            related_name='proveedor_rl_lugar_expedicion',
                                            verbose_name='Lugar de Expedicion del Id del RL')
    fecha_constitucion = models.DateTimeField(verbose_name='Fecha de Constitución', null=True, blank=True)
    fecha_inicio_actividad = models.DateTimeField(verbose_name='Fecha de Inicio de Actividad', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario', null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tercero'
        verbose_name_plural = 'Terceros'

    def empresa_to_dict(self):
        if self.empresa:
            return self.empresa.to_dict()
        else:
            return Empresa.get_default().to_dict()

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
        tercero.empresa_id = datos.get('empresa', '')
        tercero.fecha_modificacion = datetime.now()
        tercero.tipo_tercero_id = datos.get('tipo_tercero_id', '')
        tercero.centro_poblado_id = datos.get('centro_poblado_id', '')
        tercero.telefono = datos.get('telefono', '')
        tercero.fax = datos.get('fax', '')
        tercero.direccion = datos.get('direccion', '')

        return tercero


class UsuarioTercero(Persona):
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=False, blank=False)

    def __str__(self):
        return '{0} {1}'.format(self.usuario.first_name, self.usuario.last_name)

    class Meta:
        verbose_name = 'Usuario Tercero'
        verbose_name_plural = 'Usuarios Terceros'


class TipoDocumentoTercero(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)
    aplica_natural = models.BooleanField(verbose_name='Aplica Natural', null=False, blank=False)
    aplica_juridica = models.BooleanField(verbose_name='Aplica Jurídica', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Documento Tercero'
        verbose_name_plural = 'Tipos de Documentos Terceros'


class DocumentoTercero(models.Model):
    objects = ManagerGeneral()
    nombre_documento = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)
    tipo_documento = models.ForeignKey(TipoDocumentoTercero, on_delete=models.DO_NOTHING, blank=False, null=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, name='Tercero', blank=False, null=False)
    fecha_crea = models.DateTimeField(name='Fecha de Creación', blank=False, null=False)
    estado = models.BooleanField(name='Estado', blank=False, null=False)

    def __str__(self):
        return self.nombre_documento

    class Meta:
        verbose_name = 'Tipo de Contribuyente'
        verbose_name_plural = 'Tipos de Contribuyentes'


class Certificacion(models.Model):
    objects = ManagerGeneral()
    tercero = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, name='Tercero', blank=False, null=False)
    fecha_crea = models.DateField(verbose_name='Fecha de Creación', null=False, blank=False)

    def __str__(self):
        return 'Certificación de {0}'.format(self.tercero)

    class Meta:
        verbose_name = 'Certificación'
        verbose_name_plural = 'Certifiacaiones'
