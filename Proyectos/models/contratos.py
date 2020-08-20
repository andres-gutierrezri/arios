from django.contrib.auth.models import User
from django.db import models
from Administracion.models import Tercero, TipoContrato, Empresa, Proceso

# Create your models here.
from EVA.General.conversiones import string_to_date
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


class Contrato(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral(campo_texto='numero_contrato')
    numero_contrato = models.CharField(max_length=20, verbose_name='Número de contrato', null=False, blank=False)
    cliente = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, verbose_name='Cliente', null=True, blank=False)
    anho = models.IntegerField(verbose_name='Año', null=False, blank=False)
    supervisor_nombre = models.CharField(max_length=100, verbose_name='Nombre del supervisor', null=False, blank=False)
    supervisor_telefono = models.TextField(max_length=15, verbose_name='Teléfono', null=False, blank=False)
    supervisor_correo = models.EmailField(max_length=100, verbose_name='Correo del supervisor', null=False, blank=False,
                                          error_messages={'invalid': "Ingrese una dirección de correo válida"})
    residente = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Residente', null=True,
                                  blank=True)
    fecha_inicio = models.DateTimeField(verbose_name='Fecha de inicio', null=True, blank=True)
    fecha_terminacion = models.DateTimeField(verbose_name='Fecha de terminación', null=True, blank=True)
    fecha_suscripcion = models.DateTimeField(verbose_name='Fecha de suscripción', null=True, blank=False)
    valor = models.BigIntegerField(verbose_name="Valor", null=True, blank=False)
    periodicidad_informes = models.IntegerField(verbose_name='Periodicidad de informes', null=True, blank=True)
    tiempo = models.IntegerField(verbose_name='Tiempo', null=False, blank=False)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.DO_NOTHING, verbose_name='Tipo de contrato',
                                      null=True, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=False)
    proceso_a_cargo = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso a cargo',
                                        null=False, blank=False)

    def __str__(self):
        return '{0} - {1}'.format(self.numero_contrato, self.cliente)

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'Contrato':
        """
        Crea una instancia de Contrato con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el contrato.
        :return: Instacia de Contrato con la información especificada en el diccionario.
        """
        contrato = Contrato()
        contrato.numero_contrato = datos.get('numero_contrato', '')
        contrato.cliente_id = datos.get('cliente_id', '')
        contrato.anho = datos.get('rango_anho', '')
        contrato.supervisor_nombre = datos.get('supervisor_nombre', '')
        contrato.supervisor_correo = datos.get('supervisor_correo', '')
        contrato.supervisor_telefono = datos.get('supervisor_telefono', '')
        contrato.residente_id = datos.get('residente_id', '')
        contrato.fecha_inicio = string_to_date(datos.get('fecha_inicio', ''))
        contrato.fecha_terminacion = string_to_date(datos.get('fecha_terminacion', ''))
        contrato.fecha_suscripcion = string_to_date(datos.get('fecha_suscripcion', ''))
        contrato.valor = datos.get('valor', '')
        contrato.periodicidad_informes = datos.get('periodicidad_informes', None)
        contrato.tiempo = datos.get('tiempo', '')
        contrato.tipo_contrato_id = datos.get('tipo_contrato_id', '')
        contrato.empresa_id = datos.get('empresa_id', '')
        contrato.proceso_a_cargo_id = datos.get('proceso_id', '')

        return contrato
