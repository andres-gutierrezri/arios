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
    cliente = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, verbose_name='Cliente', null=False, blank=False)
    anho = models.IntegerField(verbose_name='Año', null=False, blank=False)
    residente = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Residente', null=True,
                                  blank=True)
    fecha_suscripcion = models.DateTimeField(verbose_name='Fecha de suscripción', null=True, blank=False)
    valor = models.BigIntegerField(verbose_name="Valor", null=False, blank=False)
    valor_con_iva = models.BigIntegerField(verbose_name="Valor con IVA", null=False, blank=False)
    valor_sin_iva = models.BigIntegerField(verbose_name="Valor con IVA", null=False, blank=False)
    porcentaje_a = models.DecimalField(verbose_name='Porcentaje A', decimal_places="2", max_digits="50", null=True,
                                       blank=True)
    porcentaje_i = models.DecimalField(verbose_name='Porcentaje I', decimal_places="2", max_digits="50", null=True,
                                       blank=True)
    porcentaje_u = models.DecimalField(verbose_name='Porcentaje U', decimal_places="2", max_digits="50", null=True,
                                       blank=True)
    periodicidad_informes = models.IntegerField(verbose_name='Periodicidad de informes', null=False, blank=False)
    plazo_ejecucion = models.IntegerField(verbose_name='Plazo de ejecución', null=False, blank=False)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.DO_NOTHING, verbose_name='Tipo de contrato',
                                      null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=False, blank=False)
    proceso_a_cargo = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso a cargo',
                                        null=True, blank=True)
    objeto_del_contrato = models.CharField(max_length=150, verbose_name='Objeto de contrato', null=False, blank=False)
    fecha_registro_presupuestal = models.DateTimeField(verbose_name='Fecha de registro presupuestal', null=False,
                                                       blank=False)
    numero_registro_presupuestal = models.CharField(max_length=50, verbose_name='Número de registro presupuestal',
                                                    null=False, blank=False)
    recursos_propios = models.BooleanField(verbose_name='Recursos propios', null=False, blank=False)
    origen_de_recursos = models.CharField(max_length=50, verbose_name='Origen de los recursos',
                                          null=True, blank=True)

    def __str__(self):
        return self.numero_contrato

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
