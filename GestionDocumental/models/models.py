from django.contrib.auth.models import User
from django.db import models

from Administracion.models import Tercero, TipoContrato, Empresa
from Administracion.utils import get_id_empresa_global
from EVA.General import app_date_now
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral, ModeloBase
from Proyectos.models import Contrato
from EVA import settings
from GestionDocumental.Enumeraciones import TiposActas


class ConsecutivoBase(ModeloBase, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)
    consecutivo = models.IntegerField(verbose_name='Consecutivo', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', blank=False, null=False)
    justificacion = models.CharField(max_length=100, verbose_name='Justificación', blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)

    def __str__(self):
        return self.codigo

    class Meta:
        abstract = True

    def carga_campos_crear_editar(self, request, edita):
        if edita:
            self.usuario_modifica = request.user
        else:
            self.usuario_crea = request.user
            self.empresa_id = get_id_empresa_global(request)


class ConsecutivoOficio(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    consecutivo = models.IntegerField(verbose_name='Consecutivo', null=False, blank=False)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)
    detalle = models.CharField(max_length=255, verbose_name='Detalle', null=False, blank=False)
    destinatario = models.CharField(max_length=100, verbose_name='Destinatario', null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null=False, blank=False)
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', blank=False, null=False)
    justificacion = models.CharField(max_length=100, verbose_name='Justificacion', blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)

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
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.estado = True

        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de oficios.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        if not consecutivo:
            consecutivo = self.consecutivo
        self.codigo = f'{self.proceso.sigla}-{consecutivo:03d}-{self.numero_contrato}-{app_date_now().year}'


def custom_upload_to(instance, filename):
    return '{3}/contratos/{0}/{1}.{2}'.format(app_date_now().year, instance.codigo, filename.split(".")[-1],
                                              settings.EVA_PRIVATE_MEDIA)


class ConsecutivoContrato(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral('codigo')
    numero_contrato = models.IntegerField(verbose_name='Número de Contrato', null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True, blank=True,
                                related_name='consecutivo_contrato_usuario')
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=True, blank=True)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.CASCADE, verbose_name='Tipo de Contrato',
                                      null=True, blank=True)
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio', null=False, blank=False)
    fecha_final = models.DateField(verbose_name='Fecha Final', null=True, blank=True)
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)
    fecha_crea = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=False, blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Crea',
                                     null=True, blank=True, related_name='consecutivo_contrato_usuario_crea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Modifica',
                                         null=True, blank=True, related_name='consecutivo_contrato_usuario_Modifica')
    justificacion = models.CharField(max_length=100, verbose_name='Justificacion', blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)
    ruta_archivo = models.FileField(blank=True, max_length=250, upload_to=custom_upload_to)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)

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
        consecutivo.usuario_id = datos.get('colaborador', None)
        if consecutivo.usuario_id == '':
            consecutivo.usuario_id = None
        consecutivo.tercero_id = datos.get('tercero', '')
        consecutivo.tipo_contrato_id = datos.get('tipo_contrato', '')
        consecutivo.fecha_inicio = datos.get('fecha_inicio', '')
        consecutivo.fecha_final = datos.get('fecha_final', '')
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.estado = True
        if not consecutivo.fecha_final:
            consecutivo.fecha_final = None

        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de constratos.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        if not consecutivo:
            consecutivo = self.numero_contrato
        self.codigo = f'CTO_{consecutivo:03d}-{self.sigla}-{app_date_now().year}'


class ConsecutivoReunion(ConsecutivoBase):
    fecha = models.DateField(verbose_name='Fecha', null=False, blank=False)
    tema = models.CharField(max_length=100, verbose_name='Tema', null=False, blank=False)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=True, blank=True)

    class Meta:
        verbose_name = 'Consecutivo Reunión'
        verbose_name_plural = 'Consecutivos Reuniones'

    @staticmethod
    def from_dictionary(datos: dict, request, edita=False) -> 'ConsecutivoReunion':
        """
        Crea una instancia de ConsecutivoReunion con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de Reunión.
        :return: Instacia de consecutivo de oficios con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoReunion()
        consecutivo.carga_campos_crear_editar(request, edita)
        consecutivo.tema = datos.get('tema', '')
        consecutivo.fecha = datos.get('fecha', '')
        consecutivo.descripcion = datos.get('descripcion', '')
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.estado = True

        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de reunión.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        if not consecutivo:
            consecutivo = self.consecutivo
        self.codigo = f'ACR_{consecutivo:03d}-{app_date_now():%y}'


class ConsecutivoRequerimiento(ConsecutivoBase):
    descripcion = models.CharField(max_length=1000, verbose_name='Descripción', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Requerimiento'
        verbose_name_plural = 'Consecutivos Requerimientos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoRequerimiento':
        """
        Crea una instancia de ConsecutivoOficio con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de Oficios.
        :return: Instacia de consecutivo de requerimientos de  con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoRequerimiento()
        consecutivo.contrato_id = datos.get('contrato_id', None)
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.descripcion = datos.get('descripcion', '')
        consecutivo.estado = True
        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de requerimiento.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        if not consecutivo:
            consecutivo = self.consecutivo
        anio = str(self.anio)[2:4]
        self.codigo = f'RQ_{consecutivo:03d}-{self.numero_contrato}-{anio}-{app_date_now():%y}'


class ConsecutivoPlanTrabajo(ConsecutivoBase):
    descripcion = models.CharField(max_length=1000, verbose_name='Descripción', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Plan de trabajo'
        verbose_name_plural = 'Consecutivos Plan de trabajo'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoPlanTrabajo':
        """
        Crea una instancia de ConsecutivoPlanTrabajo con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de plan de trabajo.
        :return: Instacia de consecutivo de plan de trabajo de  con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoPlanTrabajo()
        consecutivo.contrato_id = datos.get('contrato_id', None)
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.descripcion = datos.get('descripcion', '')
        consecutivo.estado = True

        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de plan de trabajo.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        if not consecutivo:
            consecutivo = self.consecutivo
        anio = str(self.anio)[2:4]
        self.codigo = f'PT_{consecutivo:03d}-{self.numero_contrato}-{anio}'


class ConsecutivoViaticosComisiones(ConsecutivoBase):
    descripcion = models.CharField(max_length=1000, verbose_name='Descripción', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Viáticos y Comisiones'
        verbose_name_plural = 'Consecutivos Viáticos y Comisiones'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoViaticosComisiones':
        """
        Crea una instancia de ConsecutivoViaticosComisiones con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de viaticos y comisiones.
        :return: Instacia de consecutivo de viaticos y comisiones de  con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoViaticosComisiones()
        consecutivo.contrato_id = datos.get('contrato_id', None)
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.descripcion = datos.get('descripcion', '')
        consecutivo.estado = True

        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de viáticos y comisiones.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        if not consecutivo:
            consecutivo = self.consecutivo
        anio = str(self.anio)[2:4]
        self.codigo = f'VT_{consecutivo:03d}-{self.numero_contrato}-{anio}-{app_date_now():%y}'


class ConsecutivoOrdenesTrabajo(ConsecutivoBase):
    fecha_inicio = models.DateField(verbose_name='Fecha Inicial')
    fecha_final = models.DateField(verbose_name='Fecha Final', null=True, blank=True)
    descripcion = models.CharField(max_length=1000, verbose_name='Descripción', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Ordenes de trabajo'
        verbose_name_plural = 'Consecutivos Ordenes de trabajo'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoOrdenesTrabajo':
        """
        Crea una instancia de ConsecutivoViaticosComisiones con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de viaticos y comisiones.
        :return: Instacia de consecutivo de viaticos y comisiones de  con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoOrdenesTrabajo()
        consecutivo.contrato_id = datos.get('contrato_id', None)
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.descripcion = datos.get('descripcion', '')
        consecutivo.fecha_inicio = datos.get('fecha_inicio', '')
        consecutivo.fecha_final = datos.get('fecha_final', '')
        consecutivo.estado = True
        if not consecutivo.fecha_final:
            consecutivo.fecha_final = None

        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de ordenes de trabajo.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        if not consecutivo:
            consecutivo = self.consecutivo
        self.codigo = f'OT_{consecutivo:03d}-{self.numero_contrato}-{app_date_now():%y}'


class ConsecutivoActasContratos(ConsecutivoBase):
    fecha_suspension = models.DateField(verbose_name='Fecha Suspensión', null=True, blank=True)
    fecha_reinicio = models.DateField(verbose_name='Fecha Reinicio', null=True, blank=True)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=False, blank=False)
    consecutivo_contrato = models.ForeignKey(ConsecutivoContrato, on_delete=models.CASCADE,
                                             verbose_name='Consecutivo Contrato', null=True, blank=True)
    tipo_acta = models.SmallIntegerField(choices=TiposActas.choices, verbose_name='Tipo de Acta',
                                         null=False, blank=False)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo acta de contrato'
        verbose_name_plural = 'Consecutivos actas de contratos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoActasContratos':
        """
        Crea una instancia de ConsecutivoViaticosComisiones con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de viaticos y comisiones.
        :return: Instacia de consecutivo de viaticos y comisiones de  con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoActasContratos()
        consecutivo.tipo_acta = datos.get('tipo_acta_id', None)
        consecutivo.consecutivo_contrato_id = datos.get('consecutivo_contrato_id', None)
        consecutivo.justificacion = datos.get('motivo', '')
        consecutivo.descripcion = datos.get('descripcion', '')
        consecutivo.fecha_suspension = datos.get('fecha_suspension', '')
        consecutivo.fecha_reinicio = datos.get('fecha_reinicio', '')
        if not consecutivo.fecha_suspension:
            consecutivo.fecha_suspension = None
        consecutivo.estado = True
        if not consecutivo.fecha_reinicio:
            consecutivo.fecha_reinicio = None
        consecutivo.estado = True

        return consecutivo

    def actualizar_codigo(self, consecutivo: int = None):
        """
        Actualiza el código del consecutivo de actas de contratos.
        :param consecutivo: Número del consecutivo, si no se especifica se toma el que tiene asignado la
        instancia.
        """
        sigla_tipo_acta = TiposActas.sigla(self.tipo_acta)
        if not consecutivo:
            consecutivo = self.consecutivo
        self.codigo = f'{sigla_tipo_acta}-{consecutivo:03d}-{app_date_now().year}'
