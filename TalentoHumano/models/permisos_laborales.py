from django.contrib.auth.models import User
from django.db import models

from EVA import settings
from EVA.General import app_date_now
from EVA.General.conversiones import string_to_datetime
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


class TipoPermiso (models.Model):
    objects = ManagerGeneral()
    tipo = models.CharField(max_length=100, verbose_name='Tipo de Permiso', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False, default=True)

    def __str__(self):
        return self.tipo

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
        permiso = TipoPermiso()
        permiso.tipo = datos.get('tipo', '')

        return permiso


def custom_upload_to(instance, filename):
    return '{3}/Permisos/Documentos/{0}/{1}/{2}'.format(app_date_now().year, instance.usuario_crea.username, filename,
                                                        settings.EVA_PRIVATE_MEDIA)


class PermisoLaboral (models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='PermisoLaboralCrea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=False, related_name='PermisoLaboralModifica')
    fecha_inicio = models.DateTimeField(verbose_name='Fecha Inicio', null=False, blank=False)
    fecha_fin = models.DateTimeField(verbose_name='Fecha Fin', null=False, blank=False)
    fecha_crea = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Crea', null=False, blank=False)
    fecha_modifica = models.DateTimeField(auto_now=True, verbose_name='Fecha Modifica', null=True, blank=False)
    tipo_permiso = models.ForeignKey(TipoPermiso, on_delete=models.DO_NOTHING, verbose_name='Tipo de Permiso',
                                     null=False, blank=False)
    jefe_inmediato = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Jefe Inmediato', null=True,
                                       blank=True)
    motivo_permiso = models.CharField(max_length=300, verbose_name='Motivo Permiso', null=False, blank=False)
    motivo_editar = models.TextField(max_length=100, verbose_name='Motivo Editar', null=False, blank=False)
    soporte = models.FileField(upload_to=custom_upload_to, verbose_name='Documento Soporte', null=False, blank=False,
                               max_length=250)
    estado_th = models.BooleanField(verbose_name='Estado TH', null=False, blank=False)
    estado_jefe = models.BooleanField(verbose_name='Estado Jefe', null=False, blank=False)
    estado_gerencia = models.BooleanField(verbose_name='Estado Gerencia', null=False, blank=False)
    motivo_th = models.CharField(max_length=300, verbose_name='Motivo TH', null=True, blank=False)
    motivo_jefe = models.CharField(max_length=300, verbose_name='Motivo Jefe', null=True, blank=False)
    motivo_gerencia = models.CharField(max_length=300, verbose_name='Motivo Gerencia', null=True, blank=False)
    remuneracion = models.BooleanField(verbose_name='Remuneración', null=False, blank=False)

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
        permiso.tipo_permiso = datos.get('tipo_permiso', '')
        permiso.fecha_inicio = string_to_datetime(datos.get('fecha_intervalo', '').split(' – ')[0], "%Y-%m-%d %H:%M")
        permiso.fecha_fin = string_to_datetime(datos.get('fecha_intervalo', '').split(' – ')[1], "%Y-%m-%d %H:%M")
        permiso.motivo_permiso = datos.get('motivo_permiso', '')
        permiso.motivo_editar = datos.get('motivo_editar', '')
        permiso.soporte = datos.get('soporte', None)

        return permiso
