from django.db import models

from Administracion.models import Persona, Cargo, Proceso, TipoContrato, CentroPoblado, Rango
from Proyectos.models import Contrato


class Empleado (Persona):
    direccion = models.CharField(max_length=100, verbose_name='Dirección', null=False, blank=False)
    talla_camisa = models.CharField(max_length=3, verbose_name="Talla de camisa", null=True, blank=False)
    talla_pantalon = models.IntegerField(verbose_name="Talla de pantalón", null=True, blank=False)
    talla_zapatos = models.IntegerField(verbose_name="Talla de zapatos", null=True, blank=False)
    eps = models.CharField(max_length=50, verbose_name='EPS', null=False, blank=False)
    arl = models.CharField(max_length=50, verbose_name='ARL', null=False, blank=False)
    pensiones_cesantias = models.CharField(max_length=100, verbose_name='Pensiones y cesantías', null=False,
                                           blank=False)
    fecha_ingreso = models.DateField(verbose_name='Fecha de ingreso', null=False, blank=False)
    fecha_examen = models.DateField(verbose_name='Fecha de examen', null=False, blank=False)
    fecha_dotacion = models.DateField(verbose_name='Fecha dotación', null=False, blank=False)
    salario = models.IntegerField(verbose_name="Salario", null=True, blank=False)
    jefe_inmediato = models.CharField(max_length=100, verbose_name='Jefe inmediato', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.DO_NOTHING, verbose_name='Contrato', null=True, blank=False)
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING, verbose_name='Cargo', null=True, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=False)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.DO_NOTHING, verbose_name='Tipo de contrato',
                                      null=True, blank=False)
    lugar_nacimiento = models.ForeignKey(CentroPoblado, on_delete=models.DO_NOTHING, verbose_name='Lugar de nacimiento',
                                         null=True, blank=False)
    rango = models.ForeignKey(Rango, on_delete=models.DO_NOTHING, verbose_name='Rango', null=True, blank=False)

    def __str__(self):
        return '{0} {1}'.format(self.usuario.first_name, self.usuario.last_name)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
