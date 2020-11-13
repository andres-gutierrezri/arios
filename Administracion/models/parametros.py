from django.db import models

from Administracion.models import Empresa
from EVA.General.modeljson import ModelDjangoExtensiones


# region Constantes grupos y subgrupos de parámetros.
G_FINANCIERO = 'FINANCIERO'
G_FINANCIERO_S_FLUJO_CAJA = 'FLUJO_CAJA'
G_FINANCIERO_S_FACELEC = 'FACTURACION_ELECTRONICA'
# endregion


# region Selecciones (Choices) para los grupos y subgrupos de parámetros
SELECCIONES_GRUPOS = [
    (G_FINANCIERO, 'Financiero')
]

SELECCIONES_SUBGRUPOS = [
    (G_FINANCIERO_S_FLUJO_CAJA, 'Flujo de caja'),
    (G_FINANCIERO_S_FACELEC, 'Facturación Electrónica')
]
# endregion


# region Constantes tipos de los parámetros.

TP_NUMERICO = 'NUMERICO'
TP_TEXTO = 'TEXTO'
TP_FECHA = 'FECHA'
TP_FECHA_HORA = 'FECHA_HORA'
TP_DECIMAL = 'DECIMAL'

# endregion


# region Selecciones (Choices) para los tipos de los parámetros
SELECCIONES_TIPOS_PARAMETROS = [
    (TP_NUMERICO, 'Numérico'),
    (TP_TEXTO, 'Texto'),
    (TP_FECHA, 'Fecha'),
    (TP_FECHA_HORA, 'Fecha y Hora'),
    (TP_DECIMAL, 'Decimal'),
]
# endregion


class Parametro(models.Model, ModelDjangoExtensiones):
    nombre = models.CharField(verbose_name="Nombre", max_length=50, null=False, blank=False)
    descripcion = models.CharField(verbose_name="Descripción", max_length=150, null=False, blank=False)
    tipo = models.CharField(choices=SELECCIONES_TIPOS_PARAMETROS, verbose_name="Tipo", max_length=50, null=False,
                            blank=False)
    valor = models.CharField(verbose_name="Valor", max_length=100, null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)
    grupo = models.CharField(choices=SELECCIONES_GRUPOS, verbose_name="Grupo", max_length=50, null=False, blank=False)
    subgrupo = models.CharField(choices=SELECCIONES_SUBGRUPOS, verbose_name="Subgrupo", max_length=50, null=False,
                                blank=False)
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Parámetro'
        verbose_name_plural = 'Parámetros'
