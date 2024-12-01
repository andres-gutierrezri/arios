from django.contrib.auth.models import User
from django.db import models

from EVA import settings
from EVA.General import app_date_now
from EVA.General.conversiones import string_to_datetime
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral, ModeloBase


class TipoPermiso(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Tipo de Permiso', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False, default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Permiso'
        verbose_name_plural = 'Tipos de Permiso'

    @staticmethod
    def from_dictionary(datos: dict) -> 'TipoPermiso':
        """
        Crea una instancia de TipoPermiso con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Tipo de Permiso.
        :return: Instancia de Tipo de Permiso con la información especificada en el diccionario.
        """
        tipo = TipoPermiso()
        tipo.nombre = datos.get('nombre', '')

        return tipo


def custom_upload_to(instance, filename):
    return '{3}/permisos/soportes/{0}/{1}/{2}'.format(app_date_now().year, instance.usuario_crea.username, filename,
                                                      settings.EVA_PRIVATE_MEDIA)


class PermisoLaboral(ModeloBase, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    fecha_inicio = models.DateTimeField(verbose_name='Fecha Inicio', null=False, blank=False)
    fecha_fin = models.DateTimeField(verbose_name='Fecha Fin', null=False, blank=False)
    tipo_permiso = models.ForeignKey(TipoPermiso, on_delete=models.DO_NOTHING, verbose_name='Tipo de Permiso',
                                     null=False, blank=False)
    tipo_permiso_otro = models.CharField(max_length=100, verbose_name='Tipo de Permiso Otro', null=True, blank=True,
                                         default='')
    jefe_inmediato = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Jefe Inmediato', null=True,
                                       blank=True)
    motivo_permiso = models.CharField(max_length=255, verbose_name='Motivo Permiso', null=False, blank=False)
    motivo_editar = models.CharField(max_length=255, verbose_name='Motivo Editar', null=False, blank=False)
    soporte = models.FileField(upload_to=custom_upload_to, verbose_name='Documento Soporte', null=True, blank=True,
                               max_length=250, default='')
    estado_empleado = models.BooleanField(verbose_name='Estado Empleado', blank=False, null=False, default=True)
    estado_rrhh = models.BooleanField(verbose_name='Estado RRHH', null=True, blank=True)
    estado_jefe = models.BooleanField(verbose_name='Estado Jefe', null=True, blank=True)
    estado_gerencia = models.BooleanField(verbose_name='Estado Gerencia', null=True, blank=True)
    descripcion_rrhh = models.CharField(max_length=300, verbose_name='Descripción RRHH', null=True, blank=True,
                                        default='')
    descripcion_jefe = models.CharField(max_length=300, verbose_name='Descripción Jefe', null=True, blank=True,
                                        default='')
    descripcion_gerencia = models.CharField(max_length=300, verbose_name='Descripción Gerencia', null=True, blank=True,
                                            default='')
    remuneracion = models.BooleanField(verbose_name='Remuneración', null=True, blank=True)

    def __str__(self):
        return self.usuario_crea

    class Meta:
        verbose_name = 'Permiso Laboral'
        verbose_name_plural = 'Permisos Laborales'

    @staticmethod
    def from_dictionary(datos: dict) -> 'PermisoLaboral':
        """
        Crea una instancia de PermisoLaboral con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Permiso Laboral.
        :return: Instancia de Permiso Laboral con la información especificada en el diccionario.
        """
        permiso = PermisoLaboral()
        permiso.tipo_permiso_id = datos.get('tipo_permiso', None)
        permiso.tipo_permiso_otro = datos.get('tipo_permiso_otro', '')
        permiso.fecha_inicio = string_to_datetime(datos.get('fecha_intervalo', '').split(' – ')[0], "%Y-%m-%d %H:%M")
        permiso.fecha_fin = string_to_datetime(datos.get('fecha_intervalo', '').split(' – ')[1], "%Y-%m-%d %H:%M")
        permiso.motivo_permiso = datos.get('motivo_permiso', '')
        permiso.motivo_editar = datos.get('motivo_editar', '')
        permiso.descripcion_rrhh = datos.get('descripcion_rrhh', '')
        permiso.descripcion_jefe = datos.get('descripcion_jefe', '')
        permiso.descripcion_gerencia = datos.get('descripcion_gerencia', '')

        return permiso
