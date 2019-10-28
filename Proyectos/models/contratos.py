from django.db import models
from Administracion.models.models import TipoContrato, Empresa
from Administracion.models import Tercero

# Create your models here.


class Contrato(models.Model):
    numero_contrato = models.CharField(max_length=20, verbose_name='Número de contrato', null=False, blank=False)
    cliente = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, verbose_name='Cliente', null=True, blank=False)
    anho = models.IntegerField(verbose_name='Año', null=False, blank=False)
    supervisor_nombre = models.CharField(max_length=100, verbose_name='Nombre del supervisor', null=False, blank=False)
    supervisor_telefono = models.TextField(max_length=15, verbose_name='Teléfono', null=False, blank=False)
    supervisor_correo = models.EmailField(max_length=100, verbose_name='Correo del supervisor', null=False, blank=False, error_messages={'invalid':"Ingrese una dirección de correo válida"})
    residente = models.CharField(max_length=100, verbose_name='Residente', null=False, blank=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inicio', null=False, blank=False)
    fecha_terminacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de terminación', null=True, blank=False)
    valor = models.BigIntegerField(verbose_name="Valor", null=True, blank=False)
    periocidad_informes = models.IntegerField(verbose_name='Periocidad de informes', null=False,
                                              blank=False)
    tiempo = models.IntegerField(verbose_name='Tiempo', null=False, blank=False)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.DO_NOTHING, verbose_name='Tipo de contrato',
                                      null=True, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=False)

    def __str__(self):
        return self.numero_contrato

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

