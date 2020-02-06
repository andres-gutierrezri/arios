from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal

from Administracion.models import Impuesto, Empresa, Tercero
from EVA.General.modeljson import ModelDjangoExtensiones


class ResolucionFacturacion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=False, blank=False)
    fecha_resolucion = models.DateField(verbose_name='Fecha de resolución', null=False, blank=False)
    numero_resolucion = models.CharField(verbose_name='Número de resolución', max_length=30, null=False, blank=False)
    numero_desde = models.IntegerField(verbose_name='Número desde', null=False, blank=False)
    numero_hasta = models.IntegerField(verbose_name='Número hasta', null=False, blank=False)
    prefijo = models.CharField(verbose_name='Prefijo', max_length=10, null=True, blank=True)
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateField(verbose_name='Fecha de Modificación', null=True, blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='ResFacCrea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=False, related_name='ResFacModifica')
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return 'Resolución # {0} desde {1} hasta {2}' \
            .format(self.numero_resolucion, self.numero_desde, self.numero_hasta)

    class Meta:
        verbose_name = 'Resolución de Facturación'
        verbose_name_plural = 'Resoluciones de Facturación'


class FacturaEncabezado(models.Model, ModelDjangoExtensiones):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=False, blank=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=False, blank=False)
    resolucion = models.ForeignKey(ResolucionFacturacion, on_delete=models.CASCADE,
                                   verbose_name='Resolución de Facturación', null=False, blank=False)
    fecha_vencimiento = models.DateField(verbose_name='Fecha de vencimiento', null=False, blank=False)
    subtotal = models.DecimalField(verbose_name='Subtotal', max_digits=12, decimal_places=2, null=False)
    can_items = models.PositiveIntegerField(verbose_name='Cantidad Items', null=False)
    numero_factura = models.PositiveIntegerField(verbose_name='Número de Factura', null=True, blank=True)
    valor_impuesto = models.DecimalField(verbose_name='Valor Impuesto', max_digits=12, decimal_places=2, null=True)
    porcentaje_administracion = models.DecimalField(verbose_name='Administración %', decimal_places=2, max_digits=5,
                                                    null=True, blank=True)
    porcentaje_imprevistos = models.DecimalField(verbose_name='Imprevistos %', decimal_places=2, max_digits=5,
                                                 null=True, blank=True)
    porcentaje_utilidad = models.DecimalField(verbose_name='Utilidad %', decimal_places=2, max_digits=5, null=True,
                                              blank=True)
    amortizacion = models.DecimalField(verbose_name='Valor Total', max_digits=12, decimal_places=2, null=True,
                                       blank=True)
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateField(verbose_name='Fecha de Modificación', null=True, blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='FacturaCrea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=False, related_name='FacturaModifica')
    estado = models.SmallIntegerField(verbose_name='Estado', null=False, blank=False)

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
            ((self.subtotal * self.porcentaje_administracion) / Decimal(100.00) if self.porcentaje_administracion is not None
             else 0.00), 2))

    @property
    def total_imprevistos(self):
        return Decimal(round(((self.subtotal * self.porcentaje_imprevistos) / Decimal(100.00) if self.porcentaje_imprevistos is not None
                      else 0.00), 2))

    @property
    def total_utilidad(self):
        return Decimal(round(((self.subtotal * self.porcentaje_utilidad) / Decimal(100.00) if self.porcentaje_utilidad is not None
                      else 0.00), 2))

    @property
    def total_amortizacion(self):
        return Decimal(round(self.amortizacion if self.amortizacion is not None else 0.00, 2))

    @property
    def total_impuesto(self):
        return Decimal(round(self.valor_impuesto if self.valor_impuesto is not None else 0.00, 2))

    @property
    def total_factura(self):
        return Decimal(round(self.subtotal + self.total_administracion + self.total_imprevistos + self.total_utilidad
                             + self.total_impuesto - self.total_amortizacion, 2))


class FacturaDetalle(models.Model):
    factura_encabezado = models.ForeignKey(FacturaEncabezado, on_delete=models.CASCADE,
                                           verbose_name='Encabezado Factura', null=False, blank=False)
    titulo = models.TextField(verbose_name='Título', max_length=250, null=False, blank=False)
    descripcion = models.TextField(verbose_name='Descripción', max_length=500, null=True, blank=True)
    cantidad = models.PositiveIntegerField(verbose_name='Cantidad', null=False, blank=False)
    valor_unitario = models.DecimalField(verbose_name='Valor Unitario', max_digits=12, decimal_places=2, null=False,
                                         blank=False)
    impuesto = models.ForeignKey(Impuesto, on_delete=models.DO_NOTHING, verbose_name='Impuesto', null=True)

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
