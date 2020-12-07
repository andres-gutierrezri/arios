from django.contrib.auth.models import User
from django.db import models
from Administracion.models import Tercero, TipoContrato, Empresa, Proceso, Municipio

# Create your models here.
from EVA.General.conversiones import string_to_datetime
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


class Contrato(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral(campo_texto='numero_contrato')
    numero_contrato = models.CharField(max_length=20, verbose_name='Número de contrato', null=False, blank=False)
    cliente = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, verbose_name='Cliente', null=False, blank=False)
    anho = models.IntegerField(verbose_name='Año', null=False, blank=False)
    residente = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Residente', null=True,
                                  blank=True)
    fecha_suscripcion = models.DateTimeField(verbose_name='Fecha de suscripción', null=False, blank=False)
    valor = models.DecimalField(verbose_name="Valor", decimal_places=2, max_digits=16, null=False, blank=False)
    valor_con_iva = models.DecimalField(verbose_name="Valor con IVA", decimal_places=2, max_digits=16,
                                        null=False, blank=False)
    valor_sin_iva = models.DecimalField(verbose_name="Valor con IVA", decimal_places=2, max_digits=16,
                                        null=False, blank=False)
    porcentaje_a = models.DecimalField(verbose_name='Porcentaje A', decimal_places=2, max_digits=5, null=True,
                                       blank=True)
    porcentaje_i = models.DecimalField(verbose_name='Porcentaje I', decimal_places=2, max_digits=5, null=True,
                                       blank=True)
    porcentaje_u = models.DecimalField(verbose_name='Porcentaje U', decimal_places=2, max_digits=5, null=True,
                                       blank=True)
    periodicidad_informes = models.IntegerField(verbose_name='Periodicidad de informes', null=False, blank=False)
    plazo_ejecucion = models.IntegerField(verbose_name='Plazo de ejecución', null=False, blank=False)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.DO_NOTHING, verbose_name='Tipo de contrato',
                                      null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=False, blank=False)
    proceso_a_cargo = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso a cargo',
                                        null=True, blank=True)
    objeto_del_contrato = models.CharField(max_length=500, verbose_name='Objeto de contrato', null=False, blank=False)
    fecha_registro_presupuestal = models.DateTimeField(verbose_name='Fecha de registro presupuestal', null=True,
                                                       blank=True)
    numero_registro_presupuestal = models.CharField(max_length=50, verbose_name='Número de registro presupuestal',
                                                    null=True, blank=True)
    recursos_propios = models.BooleanField(verbose_name='Recursos propios', null=False, blank=False)
    origen_de_recursos = models.CharField(max_length=50, verbose_name='Origen de los recursos',
                                          null=True, blank=True)

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
        contrato.anho = datos.get('anho', '')
        contrato.residente_id = datos.get('residente_id', '')
        contrato.fecha_suscripcion = string_to_datetime(datos.get('fecha_suscripcion', ''))
        contrato.valor = datos.get('valor', '')
        contrato.valor_con_iva = datos.get('valor_con_iva', '')
        contrato.valor_sin_iva = datos.get('valor_sin_iva', '')
        contrato.porcentaje_a = datos.get('porcentaje_a', '')
        contrato.porcentaje_i = datos.get('porcentaje_i', '')
        contrato.porcentaje_u = datos.get('porcentaje_u', '')
        contrato.periodicidad_informes = datos.get('periodicidad_informes', '')
        contrato.plazo_ejecucion = datos.get('plazo_ejecucion', '')
        contrato.tipo_contrato_id = datos.get('tipo_contrato_id', '')
        contrato.proceso_a_cargo_id = datos.get('proceso_id', '')
        contrato.objeto_del_contrato = datos.get('objeto_del_contrato', '')
        contrato.fecha_registro_presupuestal = datos.get('fecha_registro_presupuestal', '')
        contrato.numero_registro_presupuestal = datos.get('numero_registro_presupuestal', '')
        contrato.recursos_propios = datos.get('origen_recurso_select', '')
        contrato.origen_de_recursos = datos.get('origen_recurso', '')

        if not contrato.fecha_registro_presupuestal:
            contrato.fecha_registro_presupuestal = None

        return contrato


class FormasPago(models.Model, ModelDjangoExtensiones):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=False, blank=False)
    anticipo = models.DecimalField(verbose_name='Anticipo', decimal_places=2, max_digits=16, blank=True, null=True)
    actas_parciales = models.DecimalField(verbose_name='Actas parciales', decimal_places=2, max_digits=16,
                                          blank=True, null=True)
    liquidacion = models.DecimalField(verbose_name='Liquidación', decimal_places=2, max_digits=16,
                                      blank=True, null=True)
    forma_pago = models.IntegerField(verbose_name='Forma de Pago', blank=False, null=False)
    aplica_porcentaje = models.BooleanField(verbose_name='Aplica Porcentaje', blank=False, null=False)

    def __str__(self):
        return 'Forma de Pago para el contrato: {0}'.format(self.contrato)

    class Meta:
        verbose_name = 'Forma de Pago'
        verbose_name_plural = 'Formas de Pago'


class ContratoMunicipio(models.Model, ModelDjangoExtensiones):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato',
                                 null=False, blank=False)
    municipio = models.ForeignKey(Municipio, on_delete=models.DO_NOTHING, verbose_name='Municipio',
                                  null=False, blank=False)

    def __str__(self):
        return 'Contrato: {0} - Municipio: {1}'.format(self.contrato, self.municipio)

    class Meta:
        verbose_name = 'Contrato Municipio'
        verbose_name_plural = 'Contratos Municipios'


class ContratoVigencia(models.Model, ModelDjangoExtensiones):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato',
                                 null=False, blank=False)
    anho = models.IntegerField(verbose_name='Año', null=False, blank=False)
    valor = models.DecimalField(verbose_name='Valor', decimal_places=2, max_digits=16, null=False, blank=False)

    def __str__(self):
        return 'Vigencia del contrato {0}'.format(self.contrato)

    class Meta:
        verbose_name = 'Contrato Vigencia'
        verbose_name_plural = 'Contratos Vigencias'


class ContratoIterventoriaSupervisor(models.Model, ModelDjangoExtensiones):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato',
                                 null=False, blank=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, verbose_name='Tercero',
                                null=False, blank=False)
    tipo = models.IntegerField(verbose_name='Tipo', null=False, blank=False)

    def __str__(self):
        if self.tipo == 0:
            texto = 'Supervisor'
        else:
            texto = 'Interventor'
        return '{0} del contrato {1}: {2}'.format(texto, self.contrato, self.tercero)

    class Meta:
        verbose_name = 'Contrato Interventoria Supervisor'
        verbose_name_plural = 'Contratos Interventorias Supervisores'


class TipoGarantia(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name="Nombre", max_length=50, blank=False, null=False)
    descripcion = models.CharField(verbose_name="Descripción", max_length=50, blank=False, null=False)
    aplica_valor_smmlv = models.BooleanField(verbose_name="Aplica Valor en SMMLV", blank=False, null=False)
    aplica_amparos = models.BooleanField(verbose_name="Aplica Amparos", blank=False, null=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Garantía'
        verbose_name_plural = 'Tipos de Garantías'


class ContratoGarantia(models.Model, ModelDjangoExtensiones):
    tipo_garantia = models.ForeignKey(TipoGarantia, on_delete=models.DO_NOTHING, verbose_name="Tipo de garantía",
                                      blank=False, null=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato',
                                 null=False, blank=False)
    porcentaje_asegurado = models.DecimalField(verbose_name='Porcentaje asegurado', decimal_places=2, max_digits=5,
                                               null=True, blank=True)
    vigencia = models.IntegerField(verbose_name="Vigencia", blank=False, null=False)
    extensiva = models.BooleanField(verbose_name="Extensiva", blank=False, null=False)

    def __str__(self):
        return 'Garantía del contrato: {0}'.format(self.contrato)

    class Meta:
        verbose_name = 'Contrato Garantía'
        verbose_name_plural = 'Contratos Garantías'


class Amparos(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name="Nombre", blank="False", null="False", max_length=100)
    descripcion = models.CharField(verbose_name="Desripción", blank="False", null="False", max_length=100)
    estado = models.BooleanField(verbose_name="Estado", blank="False", null="False")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Amparo'
        verbose_name_plural = 'Amparos'


class GarantiaAmparos(models.Model, ModelDjangoExtensiones):
    garantia = models.ForeignKey(ContratoGarantia, on_delete=models.DO_NOTHING, verbose_name="Contrato garantía",
                                 blank=False, null=False)
    amparo = models.ForeignKey(Amparos, on_delete=models.DO_NOTHING, verbose_name="Contrato garantía",
                               blank=False, null=False)
    limite_asegurado = models.CharField(verbose_name="Límite asegurado", blank="False", null="False", max_length=100)

    def __str__(self):
        return 'Amparo {0} del contrato: {1}'.format(self.amparo, self.garantia.contrato)

    class Meta:
        verbose_name = 'Amparo de Garantía'
        verbose_name_plural = 'Amparos de Garantías'
