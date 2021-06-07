from attr.validators import instance_of
from django.contrib.auth.models import User
from django.db import models

import GestionDocumental
from Administracion.models import Tercero, TipoContrato, Empresa
from EVA.General import app_date_now
from EVA.General.modelmanagers import ManagerGeneral
from Proyectos.models import Contrato
from EVA import settings


class ConsecutivoOficio(models.Model):
    objects = ManagerGeneral()
    consecutivo = models.IntegerField(verbose_name='Consecutivo', null=False, blank=False)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)
    detalle = models.TextField(max_length=300, verbose_name='Detalle', null=False, blank=False)
    destinatario = models.CharField(max_length=100, verbose_name='Destinatario', null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null=False, blank=False)
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', blank=False, null=False)
    justificacion = models.CharField(max_length=100, verbose_name='Justificacion', blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Oficio'
        verbose_name_plural = 'Consecutivos Oficios'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoOficio':
        """
        Crea una instancia de ConsecutivoOficio con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de Oficios.
        :return: Instacia de consecutivo de oficios con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoOficio()
        consecutivo.contrato_id = datos.get('contrato_id', None)
        consecutivo.detalle = datos.get('detalle', '')
        consecutivo.destinatario = datos.get('destinatario', '')
        consecutivo.estado = True

        return consecutivo


def custom_upload_to(instance, filename):
    return '{3}/contratos/{0}/{1}.{2}'.format(app_date_now().year, instance.codigo, filename.split(".")[-1],
                                              settings.EVA_PRIVATE_MEDIA)


class ConsecutivoContrato(models.Model):
    objects = ManagerGeneral()
    numero_contrato = models.IntegerField(verbose_name='Número de Contrato', null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True, blank=True,
                                related_name='consecutivo_contrato_usuario')
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=True, blank=True)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.CASCADE, verbose_name='Tipo de Contrato',
                                      null=True, blank=True)
    fecha_inicio = models.DateTimeField(verbose_name='Fecha de Inicio', null=False, blank=False)
    fecha_final = models.DateTimeField(verbose_name='Fecha Final', null=True, blank=True)
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)
    fecha_crea = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=False, blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Crea',
                                     null=True, blank=True, related_name='consecutivo_contrato_usuario_crea')
    justificacion = models.CharField(max_length=100, verbose_name='Justificacion', blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)
    ruta_archivo = models.FileField(blank=True, max_length=250, upload_to=custom_upload_to)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Contrato'
        verbose_name_plural = 'Consecutivos Contratos'


    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoContrato':
        """
        Crea una instancia de ConsecutivoContrato con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de Contrato.
        :return: Instacia de consecutivo de contratos con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoContrato()
        consecutivo.usuario_id = datos.get('colaborador', '')
        consecutivo.tercero_id = datos.get('tercero', '')
        consecutivo.tipo_contrato_id = datos.get('tipo_contrato', '')
        consecutivo.fecha_inicio = datos.get('fecha_inicio', '')
        consecutivo.fecha_final = datos.get('fecha_final', '')
        consecutivo.estado = True
        if not consecutivo.fecha_final:
            consecutivo.fecha_final = None

        return consecutivo


class ConsecutivoReunion(models.Model):
    objects = ManagerGeneral()
    fecha = models.DateField(verbose_name='Fecha', null=False, blank=False)
    tema = models.CharField(max_length=100, verbose_name='Tema', null=False, blank=False)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null=False, blank=False)
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', blank=False, null=False)
    fecha_crea = models.DateField(verbose_name='Fecha de Creación', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)
    justificacion = models.CharField(max_length=100, verbose_name='Justificación', blank=True, null=True)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Reunión'
        verbose_name_plural = 'Consecutivos Reuniones'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoReunion':
        """
        Crea una instancia de ConsecutivoReunion con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de Reunión.
        :return: Instacia de consecutivo de oficios con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoReunion()
        consecutivo.tema = datos.get('tema', '')
        consecutivo.fecha = datos.get('fecha', '')
        consecutivo.descripcion = datos.get('descripcion', '')
        consecutivo.estado = True

        return consecutivo

