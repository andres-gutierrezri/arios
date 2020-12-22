from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal

from Administracion.models import Impuesto, Empresa, Tercero, UnidadMedida
from EVA.General.modeljson import ModelDjangoExtensiones


class ResolucionFacturacion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=False, blank=False)
    fecha_resolucion = models.DateField(verbose_name='Fecha de resolución', null=False, blank=False)
    numero_resolucion = models.CharField(verbose_name='Número de resolución', max_length=30, null=False, blank=False)
    numero_desde = models.IntegerField(verbose_name='Número desde', null=False, blank=False)
    numero_hasta = models.IntegerField(verbose_name='Número hasta', null=False, blank=False)
    prefijo = models.CharField(verbose_name='Prefijo', max_length=10, null=True, blank=True)
    llave_tecnica = models.CharField(verbose_name="Llave Técnica", max_length=64, null=True, blank=True)
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateField(verbose_name='Fecha de Modificación', null=True, blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='ResFacCrea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=False, related_name='ResFacModifica')
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    fecha_resolucion_fin = models.DateField(verbose_name='Fecha de resolución fin', null=False, blank=False)

    def __str__(self):
        return 'Resolución # {0} desde {1} hasta {2}' \
            .format(self.numero_resolucion, self.numero_desde, self.numero_hasta)

    class Meta:
        verbose_name = 'Resolución de Facturación'
        verbose_name_plural = 'Resoluciones de Facturación'


class FacturaEncabezado(models.Model, ModelDjangoExtensiones):
    class Estado(models.IntegerChoices):
        BORRADOR = 0
        CREADA = 1
        ERROR_ARMANANDO_FE = 2, 'Error Armando FE'
        ERROR_ENVIANDO_DIAN = 3, 'Error Enviando a la DIAN'
        RECHAZADA_DIAN = 4, 'Rechazada DIAN'
        APROBADA_DIAN = 5, 'Aprobada DIAN'
        ERROR_ARMANDO_AD = 6, 'Error Armando AD'
        ERROR_GENERANDO_RG = 7, 'Error Generando RG'
        ERROR_ARMANDO_ZIP = 8, 'Error Armando ZIP'
        ERROR_ENVIADO_CORREO = 9.
        ENVIADA_CLIENTE = 10, 'Enviada al Cliente'
        ACUSE_RECIBO_CLIENTE = 11
        RECHAZADA_CLIENTE = 12
        ACEPTADA_CLIENTE = 13
        ENVIADA_MODO_HABILITACION = 14, 'Enviada en Modo Habilitación'
        ANULADA = 31
        ERROR_ARMANANDO_NC = 32, 'Error Armando NC'
        ERROR_ENVIANDO_DIAN_NC = 33, 'Error Enviando a la DIAN NC'
        RECHAZADA_DIAN_NC = 34, 'Rechazada DIAN NC'
        APROBADA_DIAN_NC = 35, 'Aprobada DIAN NC'
        ERROR_ARMANDO_AD_NC = 36, 'Error Armando AD NC'
        ERROR_GENERANDO_RG_NC = 37, 'Error Generando RG NC'
        ERROR_ARMANDO_ZIP_NC = 38, 'Error Armando ZIP NC'
        ERROR_ENVIADO_CORREO_NC = 39.
        ENVIADA_CLIENTE_NC = 40, 'NC Enviada al Cliente'
        ACUSE_RECIBO_CLIENTE_NC = 41
        RECHAZADA_CLIENTE_NC = 42
        ACEPTADA_CLIENTE_NC = 43
        ENVIADA_MODO_HABILITACION_NC = 44, 'Enviada en Modo Habilitación NC'
        NOTA_DEBITO = 60


    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=False, blank=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=False, blank=False)
    resolucion = models.ForeignKey(ResolucionFacturacion, on_delete=models.CASCADE,
                                   verbose_name='Resolución de Facturación', null=False, blank=False)
    fecha_vencimiento = models.DateField(verbose_name='Fecha de vencimiento', null=False, blank=False)
    subtotal = models.DecimalField(verbose_name='Subtotal', max_digits=12, decimal_places=2, null=False)
    can_items = models.PositiveIntegerField(verbose_name='Cantidad Items', null=False)
    numero_factura = models.PositiveIntegerField(verbose_name='Número de Factura', null=True, blank=True)
    valor_impuesto = models.DecimalField(verbose_name='Valor Impuesto', max_digits=12, decimal_places=2, null=True)
    base_impuesto = models.DecimalField(verbose_name='Base Impuesto', max_digits=12, decimal_places=2, null=True)
    porcentaje_administracion = models.DecimalField(verbose_name='Administración %', decimal_places=2, max_digits=5,
                                                    null=True, blank=True)
    porcentaje_imprevistos = models.DecimalField(verbose_name='Imprevistos %', decimal_places=2, max_digits=5,
                                                 null=True, blank=True)
    porcentaje_utilidad = models.DecimalField(verbose_name='Utilidad %', decimal_places=2, max_digits=5, null=True,
                                              blank=True)
    amortizacion = models.DecimalField(verbose_name='Valor de la Amortización', max_digits=12, decimal_places=2,
                                       null=True, blank=True)
    amortizacion_id = models.CharField(verbose_name='Id de la Amortización',  max_length=150, null=True, blank=True)
    amortizacion_fecha = models.DateField(verbose_name='Fecha de la Amortización',
                                          null=True, blank=True)
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateField(verbose_name='Fecha de Modificación', null=True, blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='FacturaCrea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=False, related_name='FacturaModifica')
    estado = models.IntegerField(choices=Estado.choices, verbose_name='Estado', null=False, blank=False)
    total = models.DecimalField(verbose_name='Total', max_digits=12, decimal_places=2, null=False)
    cufe = models.CharField(verbose_name='CUFE', max_length=96, null=True, blank=True)
    total_letras = models.CharField(verbose_name='Total en Letras', max_length=250, null=False, blank=False)
    nombre_archivo_fe = models.CharField(verbose_name='Nombre del archivo de la factura electrónica', max_length=50,
                                         null=True, blank=True)
    nombre_archivo_zip = models.CharField(verbose_name='Nombre del archivo ZIP validado ', max_length=50,
                                          null=True, blank=True)
    nombre_archivo_ad = models.CharField(verbose_name='Nombre del archivo Attached Document', max_length=50,
                                         null=True, blank=True)
    forma_pago = models.SmallIntegerField(verbose_name='Forma de pago', null=False, blank=False, default=2)
    medio_pago = models.SmallIntegerField(verbose_name='Medio de pago', null=False, blank=False, default=1)

    observaciones = models.TextField(verbose_name='Observaciones', max_length=1000, null=True, blank=True)
    fecha_anulacion = models.DateField(verbose_name='Fecha de Anulación', null=True, blank=True)

    nombre_archivo_nc = models.CharField(verbose_name='Nombre del archivo de la nota crédito', max_length=50,
                                         null=True, blank=True)
    nombre_archivo_zip_nc = models.CharField(verbose_name='Nombre del archivo ZIP validado NC', max_length=50,
                                             null=True, blank=True)
    nombre_archivo_ad_nc = models.CharField(verbose_name='Nombre del archivo Attached Documen NCt', max_length=50,
                                            null=True, blank=True)
    motivo_anulacion = models.TextField(verbose_name='Motivo anulación', max_length=1000, null=True, blank=True)
    cude = models.CharField(verbose_name='CUFE', max_length=96, null=True, blank=True)
    observaciones_anulacion = models.TextField(verbose_name='Observaciones Anulacion', max_length=1000, null=True,
                                               blank=True)

    def __str__(self):
        return 'Factura # {0}'.format(self.numero_factura)

    class Meta:
        verbose_name = 'Encabezado Factura'
        verbose_name_plural = 'Encabezados Facturas'
        unique_together = ('empresa', 'numero_factura')

    @property
    def is_aplica_aiu(self):
        return not ((self.porcentaje_administracion is None) and (self.porcentaje_imprevistos is None)
                    and (self.porcentaje_utilidad is None))

    @property
    def is_amortizacion(self):
        return self.amortizacion is not None

    @property
    def total_administracion(self):
        return Decimal(round(
            (Decimal(self.subtotal * self.porcentaje_administracion) / Decimal(100.00) if
             self.porcentaje_administracion is not None
             else Decimal(0.00)), 2))

    @property
    def total_imprevistos(self):
        return Decimal(round((Decimal(self.subtotal * self.porcentaje_imprevistos) / Decimal(100.00) if
                              self.porcentaje_imprevistos is not None else Decimal(0.00)), 2))

    @property
    def total_utilidad(self):
        return Decimal(round((Decimal(self.subtotal * self.porcentaje_utilidad) / Decimal(100.00) if
                              self.porcentaje_utilidad is not None else Decimal(0.00)), 2))

    @property
    def total_amortizacion(self):
        return Decimal(round(self.amortizacion if self.amortizacion is not None else Decimal(0.00), 2))

    @property
    def total_impuesto(self):
        return Decimal(round(self.valor_impuesto if self.valor_impuesto is not None else Decimal(0.00), 2))

    @property
    def total_factura(self):
        return Decimal(round(Decimal(self.subtotal) + self.total_administracion + self.total_imprevistos +
                             self.total_utilidad + self.total_impuesto - self.total_amortizacion, 2))


class FacturaDetalle(models.Model):
    factura_encabezado = models.ForeignKey(FacturaEncabezado, on_delete=models.CASCADE,
                                           verbose_name='Encabezado Factura', null=False, blank=False)
    titulo = models.TextField(verbose_name='Título', max_length=250, null=False, blank=False)
    descripcion = models.TextField(verbose_name='Descripción', max_length=500, null=True, blank=True)
    cantidad = models.PositiveIntegerField(verbose_name='Cantidad', null=False, blank=False)
    valor_unitario = models.DecimalField(verbose_name='Valor Unitario', max_digits=12, decimal_places=2, null=False,
                                         blank=False)
    valor_total = models.DecimalField(verbose_name='Valor Total', max_digits=12, decimal_places=2, null=False,
                                      blank=False)
    valor_impuesto = models.DecimalField(verbose_name='Valor Impuesto', max_digits=12, decimal_places=2, null=False,
                                         blank=False)
    impuesto = models.ForeignKey(Impuesto, on_delete=models.DO_NOTHING, verbose_name='Impuesto', null=True)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.DO_NOTHING, verbose_name='Unidad de Medida',
                                      null=False, blank=False, default='94')

    def __str__(self):
        return 'Detalle Factura # {0})'.format(self.id)

    class Meta:
        verbose_name = 'Detalle Factura'
        verbose_name_plural = 'Detalles Factura'


class FacturaImpuesto(models.Model):
    factura_encabezado = models.ForeignKey(FacturaEncabezado, on_delete=models.CASCADE,
                                           verbose_name='Encabezado Factura', null=False, blank=False)
    impuesto = models.ForeignKey(Impuesto, on_delete=models.DO_NOTHING, verbose_name='Impuesto', null=True, blank=True)
    valor_base = models.DecimalField(verbose_name='Valor Unitario', max_digits=12, decimal_places=2, null=False,
                                     blank=False)
    valor_impuesto = models.DecimalField(verbose_name='Valor Unitario', max_digits=12, decimal_places=2, null=True,
                                         blank=True)

    def __str__(self):
        return 'Impuesto Factura base {0}, valor {1})'.format(self.valor_base, self.valor_impuesto)

    class Meta:
        verbose_name = 'Impuesto Factura'
        verbose_name_plural = 'Impuestos Factura'
