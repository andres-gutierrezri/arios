from django.db import models
from datetime import datetime
from EVA.General.conversiones import string_to_date
from django.contrib.auth.models import User
# Create your models here.
from Administracion.models import Empresa, Proceso
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


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
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cadena de aprobación encabezado'
        verbose_name_plural = 'Cadenas de aprobaciones encabezados'


class Documento(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    codigo = models.CharField(max_length=20, verbose_name='Código', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    version = models.CharField(max_length=4, verbose_name='Versión', null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de aprobación', null=True, blank=False)
    grupo_documento = models.ForeignKey(GrupoDocumento, on_delete=models.DO_NOTHING,
                                        verbose_name='Grupo de documento', null=True, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        unique_together = ('codigo', 'version', 'grupo_documento', 'proceso')

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
        documento.version = datos.get('version', '')
        documento.cadena_aprobacion_id = datos.get('cadena_aprobacion_id', '')
        documento.grupo_documento_id = datos.get('grupo_documento_id', '')
        documento.proceso_id = datos.get('proceso_id', '')
        documento.archivo = datos.get('archivo', '')

        return documento


class Archivo(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    ruta = models.CharField(max_length=100, verbose_name='Ruta', null=False, blank=False)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha', null=False, blank=False)
    hash_Archivo = models.CharField(max_length=100, verbose_name='Hash', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    notas = models.CharField(max_length=100, verbose_name='Notas', null=False, blank=False)
    documento = models.ForeignKey(Documento, on_delete=models.DO_NOTHING, verbose_name='Documento', null=True,
                                  blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Documento', null=True, blank=False)

    def __str__(self):
        return self.nombre

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
        archivo.nombre = datos.get('nombre', '')
        archivo.ruta = datos.get('ruta', '')
        archivo.fecha = datetime.now()
        archivo.hash_Archivo = datos.get('hash_archivo', '')
        archivo.estado = datos.get('estado', 'False') == 'True'
        archivo.notas = datos.get('notas', '')
        archivo.cadena_aprobacion_id = datos.get('cadena_aprobacion_id', '')
        archivo.documento_id = datos.get('documento_id', '')

        return archivo

