import calendar
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, F

from Administracion.utils import get_id_empresa_global
from Administracion.models import Proceso, Empresa
from EVA.General.modelmanagers import ManagerGeneral
from Proyectos.models import Contrato


class TipoMovimiento(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=30, null=False, blank=False)
    descripcion = models.CharField(verbose_name='Descripción', max_length=200, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Movimiento'
        verbose_name_plural = 'Tipos de Movimientos'

    # Estados Fijos
    COSTOS = 1
    GASTOS = 2
    INGRESOS = 3


class CategoriaMovimiento(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=60, null=False, blank=False)
    descripcion = models.CharField(verbose_name='Descripción', max_length=200, null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False, default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Categoria de Movimiento'
        verbose_name_plural = 'Categorias de Movimientos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'CategoriaMovimiento':
        """
        Crea una instancia de Categoría de Movimiento con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear la Categoría de Movimiento.
        :return: Instacia de entidad Categoria de Movimiento con la información especificada en el diccionario.
        """
        categoria_movimiento = CategoriaMovimiento()
        categoria_movimiento.nombre = datos.get('nombre', '')
        categoria_movimiento.descripcion = datos.get('descripcion', '')

        return categoria_movimiento


class SubTipoMovimiento(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=60, null=False, blank=False)
    descripcion = models.CharField(verbose_name='Descripción', max_length=200, null=False, blank=False)
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.DO_NOTHING, verbose_name='Tipo de Movimiento',
                                        null=False, blank=False)
    categoria_movimiento = models.ForeignKey(CategoriaMovimiento, on_delete=models.DO_NOTHING, null=False, blank=False,
                                             verbose_name='Categoría de Movimiento')
    protegido = models.BooleanField(verbose_name='Protegido', blank=False, null=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False, default=True)
    solo_contrato = models.BooleanField(verbose_name='Solo Contrato', blank=False, null=False)
    solo_proceso = models.BooleanField(verbose_name='Solo Proceso', blank=False, null=False)

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
        subtipo_movimiento.categoria_movimiento_id = datos.get('categoria_movimiento_id', '')
        subtipo_movimiento.protegido = datos.get('protegido', 'False') == 'True'

        return subtipo_movimiento


class EstadoFlujoCaja(models.Model):
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


class FlujoCajaEncabezadoManager(ManagerGeneral):
    def get_xa_select_x_contrato(self, request) -> QuerySet:
        return super().get_queryset()\
            .filter(contrato__isnull=False, contrato__empresa_id=get_id_empresa_global(request))\
            .values(campo_valor=F('id'), campo_texto=F('contrato__numero_contrato'))

    def get_xa_select_x_proceso(self, request) -> QuerySet:
        return super().get_queryset()\
            .filter(proceso__isnull=False, proceso__empresa_id=get_id_empresa_global(request)) \
            .values(campo_valor=F('id'), campo_texto=F('proceso__nombre'))

    def get_flujos_x_contrato(self, request) -> QuerySet:
        return super().get_queryset().filter(contrato__isnull=False, contrato__empresa_id=get_id_empresa_global(request))

    def get_flujos_x_proceso(self, request) -> QuerySet:
        return super().get_queryset().filter(proceso__isnull=False, proceso__empresa_id=get_id_empresa_global(request))

    def get_id_flujos_contratos(self, request) -> list:
        return list(super().get_queryset()
                    .filter(contrato__isnull=False, contrato__empresa_id=get_id_empresa_global(request))
                    .values_list('id', flat=True))

    def get_id_flujos_procesos(self, request) -> list:
        return list(super().get_queryset()
                    .filter(proceso__isnull=False, proceso__empresa_id=get_id_empresa_global(request))
                    .values_list('id', flat=True))


class FlujoCajaEncabezado(models.Model):
    objects = FlujoCajaEncabezadoManager()
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, verbose_name='Proceso',
                                null=True, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato',
                                 null=True, blank=False)
    estado = models.ForeignKey(EstadoFlujoCaja, on_delete=models.DO_NOTHING, verbose_name='Estado',
                               null=False, blank=False)
    fecha_crea = models.DateTimeField(verbose_name='Fecha de Creación', null=False, blank=False)

    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', blank=False, null=True)

    def __str__(self):
        return '{0} - {1}'.format(self.proceso, self.contrato)

    class Meta:
        verbose_name = 'Flujo de Caja Encabezado'
        verbose_name_plural = 'Flujos de Cajas Encabezados'
        permissions = (("can_gestion_flujos_de_caja", "Can gestion de flujos de caja"),
                       )


class EstadoFCDetalle(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=30, null=False, blank=False)
    descripcion = models.CharField(verbose_name='Descripción', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Estado de Flujo de Caja Detalle'
        verbose_name_plural = 'Estados de Flujos de Cajas Detalles'

    # Estados Fijos
    VIGENTE = 1
    EDITADO = 2
    OBSOLETO = 3
    ELIMINADO = 4


class FlujoCajaDetalle(models.Model):
    fecha_movimiento = models.DateTimeField(verbose_name='Fecha de Creación', max_length=100, null=False, blank=False)
    subtipo_movimiento = models.ForeignKey(SubTipoMovimiento, on_delete=models.DO_NOTHING,
                                           verbose_name='SubTipo de Movimiento', null=False, blank=False)
    valor = models.DecimalField(verbose_name='Valor', max_digits=13, decimal_places=2, null=False, blank=False)
    tipo_registro = models.IntegerField(verbose_name='Tipo Registro', blank=False, null=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Crea',
                                     null=False, blank=False, related_name='%(app_label)s_%(class)s_usuario_crea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False, verbose_name='Usuario Modifica',
                                         blank=False, related_name='%(app_label)s_%(class)s_usuario_modifica')
    flujo_caja_enc = models.ForeignKey(FlujoCajaEncabezado, on_delete=models.DO_NOTHING,
                                       verbose_name='Fluja de Caja Encabezado', null=False, blank=False)
    fecha_crea = models.DateTimeField(verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modifica = models.DateTimeField(verbose_name='Fecha de Modificación', null=False, blank=False)
    flujo_detalle = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Flujo Detalle',
                                      null=True, blank=True)
    estado = models.ForeignKey(EstadoFCDetalle, on_delete=models.DO_NOTHING, verbose_name='Estado',
                               null=False, blank=False)
    comentarios = models.CharField(verbose_name='Comentarios', max_length=100, null=True, blank=True)
    motivo_edicion = models.CharField(verbose_name='Motivo', max_length=100, null=True, blank=True)

    def __str__(self):
        return 'Flujo de Caja {0} - Detalle: {1}'.format(self.flujo_caja_enc, self.id)

    class Meta:
        verbose_name = 'Flujo de Caja Detalle'
        verbose_name_plural = 'Flujos de Cajas Detalles'

    @staticmethod
    def from_dictionary(datos: dict) -> 'FlujoCajaDetalle':
        """
        Crea una instancia de Flujo de Caja Detalle con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el registro de Flujo de Caja Detalle.
        :return: Instacia de entidad Flujo de Caja Detalle con la información especificada en el diccionario.
        """
        flujo_caja_detalle = FlujoCajaDetalle()
        flujo_caja_detalle.fecha_movimiento = datos.get('fecha_movimiento', '')
        flujo_caja_detalle.subtipo_movimiento_id = datos.get('subtipo_movimiento_id', '')
        flujo_caja_detalle.valor = datos.get('valor', '')
        flujo_caja_detalle.comentarios = datos.get('comentarios', '')

        return flujo_caja_detalle


class CorteFlujoCaja(models.Model):
    flujo_caja_enc = models.ForeignKey(FlujoCajaEncabezado, on_delete=models.DO_NOTHING,
                                       verbose_name='Flujo de Caja Encabezado', null=False, blank=False)
    fecha_corte = models.DateField(verbose_name='Fecha de Corte', null=False, blank=False)

    def __str__(self):
        return '{0} - Fecha de Corte: {1}'.format(self.flujo_caja_enc, self.fecha_corte)

    class Meta:
        verbose_name = 'Corte de Flujo de Caja'
        verbose_name_plural = 'Cortes de Flujos de Cajas'

