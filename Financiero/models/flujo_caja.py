from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from Administracion.models import Proceso
from EVA.General.modelmanagers import ManagerGeneral
from Proyectos.models import Contrato


class TipoMovimiento(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=30, null=False, blank=False)
    descripcion = models.CharField(verbose_name='Descripción', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Movimiento'
        verbose_name_plural = 'Tipos de Movimientos'


class SubTipoMovimiento(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=30, null=False, blank=False)
    descripcion = models.CharField(verbose_name='Descripción', max_length=100, null=False, blank=False)
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.DO_NOTHING, verbose_name='Tipo de Movimiento',
                                        null=False, blank=False)
    protegido = models.BooleanField(verbose_name='Protegido', blank=False, null=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False, default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Sub-Tipo de Movimiento'
        verbose_name_plural = 'Sub-Tipos de Movimientos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'SubTipoMovimiento':
        """
        Crea una instancia de Subtipo de Movimiento con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear El Subtipo de Movimiento.
        :return: Instacia de entidad Subtipo de Movimiento con la información especificada en el diccionario.
        """
        subtipo_movimiento = SubTipoMovimiento()
        subtipo_movimiento.nombre = datos.get('nombre', '')
        subtipo_movimiento.descripcion = datos.get('descripcion', '')
        subtipo_movimiento.tipo_movimiento_id = datos.get('tipo_movimiento_id', '')
        subtipo_movimiento.protegido = datos.get('protegido', 'False') == 'True'

        return subtipo_movimiento


class EstadoFC(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=30, null=False, blank=False)
    descripcion = models.CharField(verbose_name='Descripción', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Estado de Flujo de Caja'
        verbose_name_plural = 'Estados de Flujos de Cajas'

    # Estados Fijos
    ALIMENTACION = 1
    EJECUCION = 2


class FlujoCajaEncabezado(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, verbose_name='Proceso',
                                null=True, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato',
                                 null=True, blank=False)
    estado = models.ForeignKey(EstadoFC, on_delete=models.DO_NOTHING, verbose_name='Estado',
                               null=False, blank=False)
    fecha_crea = models.DateTimeField(verbose_name='Fecha de Creación', null=False, blank=False)

    def __str__(self):
        return '{0} - {1}'.format(self.proceso, self.contrato)

    class Meta:
        verbose_name = 'Flujo de Caja Encabezado'
        verbose_name_plural = 'Flujos de Cajas Encabezados'


class FlujoCajaDetalle(models.Model):
    fecha_movimiento = models.DateTimeField(verbose_name='Fecha de Creación', max_length=100, null=False, blank=False)
    subtipo_movimiento = models.ForeignKey(SubTipoMovimiento, on_delete=models.CASCADE,
                                           verbose_name='SubTipo de Movimiento', null=False, blank=False)
    valor = models.IntegerField(verbose_name='Valor', blank=False, null=False)
    tipo_registro = models.IntegerField(verbose_name='Tipo Registro', blank=False, null=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Crea',
                                     null=False, blank=False, related_name='%(app_label)s_%(class)s_usuario_crea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False, verbose_name='Usuario Modifica',
                                         blank=False, related_name='%(app_label)s_%(class)s_usuario_modifica')
    flujo_caja_enc = models.ForeignKey(FlujoCajaEncabezado, on_delete=models.DO_NOTHING,
                                       verbose_name='Fluja de Caja Encabezado', null=False, blank=False)
    fecha_crea = models.DateTimeField(verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modifica = models.DateTimeField(verbose_name='Fecha de Modificación', null=False, blank=False)

    def __str__(self):
        return 'Flujo de Caja {0} - Detalle: {1}'.format(self.flujo_caja_enc, self.id)

    class Meta:
        verbose_name = 'Flujo de Caja Detalle'
        verbose_name_plural = 'Flujos de Cajas Detalles'


def fecha_corte_default():
    return datetime.strptime('{0}-{1}-10'.format(datetime.now().year, datetime.now().month + 1), "%Y-%m-%d")


class CorteFlujoCaja(models.Model):
    flujo_caja_enc = models.ForeignKey(FlujoCajaEncabezado, on_delete=models.CASCADE,
                                       verbose_name='Flujo de Caja Encabezado', null=False, blank=False)
    fecha_corte = models.DateField(verbose_name='Fecha de Corte', null=False, blank=False,
                                   default=fecha_corte_default)

    def __str__(self):
        return '{0} - Fecha de Corte: {1}'.format(self.flujo_caja_enc, self.fecha_corte)

    class Meta:
        verbose_name = 'Corte de Flujo de Caja'
        verbose_name_plural = 'Cortes de Flujos de Cajas'

