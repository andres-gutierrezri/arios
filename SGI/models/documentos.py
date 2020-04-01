from decimal import Decimal

from django.db import models
from datetime import datetime
from EVA.General.conversiones import string_to_date
from django.contrib.auth.models import User
# Create your models here.
from Administracion.models import Empresa, Proceso
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from TalentoHumano.models import Colaborador


class GrupoDocumento(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Grupo de documento'
        verbose_name_plural = 'Grupos de documentos'


class CadenaAprobacionEncabezado(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre', null=False, blank=False)
    fecha_creacion = models.DateTimeField(verbose_name='Fecha de Creación', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False, default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cadena de aprobación encabezado'
        verbose_name_plural = 'Cadenas de aprobaciones encabezados'


class CadenaAprobacionDetalle(models.Model):
    usuario = models.ForeignKey(Colaborador, on_delete=models.DO_NOTHING, verbose_name='Usuario', null=True,
                                blank=False)
    orden = models.SmallIntegerField(verbose_name='Orden', null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de Aprobación', null=False, blank=False)

    def __str__(self):
        return self.usuario.usuario.first_name

    class Meta:
        verbose_name = 'Detalle de cadena de aprobación'
        verbose_name_plural = 'Detalles de cadenas de aprobaciones'


class Documento(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    codigo = models.CharField(max_length=20, verbose_name='Código', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    version_actual = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Versión Actual',
                                         null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de aprobación', null=True, blank=False)
    grupo_documento = models.ForeignKey(GrupoDocumento, on_delete=models.DO_NOTHING,
                                        verbose_name='Grupo de documento', null=True, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=False)

    def __str__(self):
        return '{0} {1}'.format(self.codigo, self.nombre) +\
               (' v{:.1f}'.format(self.version_actual) if self.version_actual != 0 else '')

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        unique_together = ('codigo', 'grupo_documento', 'proceso'), ('nombre', 'grupo_documento', 'proceso')

    @staticmethod
    def from_dictionary(datos: dict) -> 'Documento':
        """
        Crea una instancia de Documento con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el docuemento.
        :return: Instacia de Documento con la información especificada en el diccionario.
        """
        documento = Documento()
        documento.nombre = datos.get('nombre', '')
        documento.codigo = datos.get('codigo', '')
        documento.fecha_modificacion = datetime.now()
        documento.version_actual = datos.get('version_actual', '')
        documento.cadena_aprobacion_id = datos.get('cadena_aprobacion_id', '')
        documento.grupo_documento_id = datos.get('grupo_documento_id', '')
        documento.proceso_id = datos.get('proceso_id', '')

        return documento

    @property
    def version_minima_siguiente(self):
        return '{0:.1f}'.format(self.version_actual + Decimal('0.1'))


class EstadoArchivo(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Estado de Archivo'
        verbose_name_plural = 'Estados de Archivos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'EstadoArchivo':
        """
        Crea una instancia de Archivo con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el docuemento.
        :return: Instacia de Documento con la información especificada en el diccionario.
        """
        estado = EstadoArchivo()
        estado.nombre = datos.get('nombre', '')
        estado.descripcion = datos.get('descripcion', '')

        return estado
    #Estados Fijos
    PENDIENTE = 0
    APROBADO = 1
    OBSOLETO = 2
    RECHAZADO = 3


def custom_upload_to(instance, filename):
    return 'SGI/Documentos/{0:d}/{1:d}/{2} {3} v{4:.1f}.{5}'\
        .format(instance.documento.proceso.empresa.id, instance.documento.proceso.id, instance.documento.codigo,
                instance.documento.nombre, instance.version, filename.split(".")[1])


class Archivo(models.Model):
    objects = ManagerGeneral()
    documento = models.ForeignKey(Documento, on_delete=models.DO_NOTHING, verbose_name='Documento', null=True,
                                  blank=False)
    version = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Versión',
                                  null=False, blank=False)
    notas = models.CharField(max_length=100, verbose_name='Notas', null=False, blank=False)
    fecha_documento = models.DateField(verbose_name='Fecha del Documento', null=False, blank=False)
    archivo = models.FileField(upload_to=custom_upload_to, blank=True)
    hash = models.CharField(max_length=300, verbose_name='Hash', null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de aprobación', null=True, blank=False)
    estado = models.ForeignKey(EstadoArchivo, on_delete=models.DO_NOTHING, verbose_name='Estado de Archivo', null=False,
                               blank=False)

    def __str__(self):
        return self.documento.nombre

    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'Archivo':
        """
        Crea una instancia de Archivo con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el docuemento.
        :return: Instacia de Documento con la información especificada en el diccionario.
        """
        archivo = Archivo()
        archivo.documento_id = datos.get('documento_id', '')
        archivo.version = datos.get('version', '')
        archivo.notas = datos.get('notas', '')
        archivo.fecha_documento = datos.get('fecha_documento', '')
        archivo.archivo = datos.get('archivo', None)
        archivo.hash = datos.get('hash', '')
        archivo.cadena_aprobacion_id = datos.get('cadena_aprobacion_id', '')
        archivo.estado_id = datos.get('estado_id', '')

        return archivo

