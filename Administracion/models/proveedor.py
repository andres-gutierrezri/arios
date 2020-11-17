from django.db import models

from Administracion.models import Tercero
from Financiero.models.models import ActividadEconomica


class ActividadEconomicaTercero(models.Model):
    actividad_economica = models.ForeignKey(ActividadEconomica, on_delete=models.DO_NOTHING, null=False, blank=False,
                                            verbose_name='Actividad Económica')
    proveedor = models.ForeignKey(Tercero, on_delete=models.DO_NOTHING, verbose_name='Proveedor',
                                  null=False, blank=False)

    def __str__(self):
        return 'Actividad {0} - {1}'.format(self.actividad_economica, self.proveedor)

    class Meta:
        verbose_name = 'Actividad Económica de Proveedor'
        verbose_name_plural = 'Actividades Económicas de Los Proveedores'
