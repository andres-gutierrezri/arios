from django.db import models

from Administracion.models import Persona, Cargo, Proceso, TipoContrato, CentroPoblado, Rango
from EVA.General.conversiones import string_to_date
from EVA.General.modeljson import ModelDjangoExtensiones
from Proyectos.models import Contrato
from TalentoHumano.models import EntidadesCAFE
from TalentoHumano.models.entidades_cafe import EntidadesManger


class Colaboradores (Persona, ModelDjangoExtensiones):
    objects = EntidadesManger()
    direccion = models.CharField(max_length=100, verbose_name='Dirección', null=False, blank=False)
    talla_camisa = models.CharField(max_length=3, verbose_name="Talla de camisa", null=True, blank=False)
    talla_pantalon = models.IntegerField(verbose_name="Talla de pantalón", null=True, blank=False)
    talla_zapatos = models.IntegerField(verbose_name="Talla de zapatos", null=True, blank=False)
    eps = models.ForeignKey(EntidadesCAFE, on_delete=models.DO_NOTHING, verbose_name='EPS', null=False, blank=False,
                            related_name='%(app_label)s_%(class)s_eps')
    arl = models.ForeignKey(EntidadesCAFE, on_delete=models.DO_NOTHING, verbose_name='ARL', null=False, blank=False,
                            related_name='%(app_label)s_%(class)s_arl')
    afp = models.ForeignKey(EntidadesCAFE, on_delete=models.DO_NOTHING, verbose_name='AFP', null=False, blank=False,
                            related_name='%(app_label)s_%(class)s_afp')
    caja_compensacion = models.ForeignKey(EntidadesCAFE, on_delete=models.DO_NOTHING,
                                          verbose_name='Caja de compensación', null=False, blank=False,
                                          related_name='%(app_label)s_%(class)s_caja_compensacion')
    fecha_ingreso = models.DateField(verbose_name='Fecha de ingreso', null=False, blank=False)
    fecha_examen = models.DateField(verbose_name='Fecha de examen', null=False, blank=False)
    fecha_dotacion = models.DateField(verbose_name='Fecha de dotación', null=False, blank=False)
    salario = models.IntegerField(verbose_name="Salario", null=True, blank=False)
    jefe_inmediato = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Jefe inmediato', null=True,
                                       blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.DO_NOTHING, verbose_name='Contrato', null=False,
                                 blank=False)
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING, verbose_name='Cargo', null=False, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=False, blank=False)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.DO_NOTHING, verbose_name='Tipo de contrato',
                                      null=False, blank=False)
    lugar_nacimiento = models.ForeignKey(CentroPoblado, on_delete=models.DO_NOTHING, verbose_name='Lugar de nacimiento',
                                         null=False, blank=False)
    rango = models.ForeignKey(Rango, on_delete=models.DO_NOTHING, verbose_name='Rango', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return '{0} {1}'.format(self.usuario.first_name, self.usuario.last_name)

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'

    @staticmethod
    def from_dictionary(datos: dict) -> 'Colaboradores':
        """
        Crea una instancia de Colaboradores con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear Colaboradores.
        :return: Instacia de entidad colaboradores con la información especificada en el diccionario.
        """
        colaborador = Colaboradores()
        colaborador.direccion = datos.get('direccion', '')
        colaborador.talla_camisa = datos.get('talla_camisa', '')
        colaborador.talla_zapatos = datos.get('talla_zapatos', '')
        colaborador.talla_pantalon = datos.get('talla_pantalon', '')
        colaborador.eps_id = datos.get('eps_id', '')
        colaborador.arl_id = datos.get('arl_id', '')
        colaborador.afp_id = datos.get('afp_id', '')
        colaborador.caja_compensacion_id = datos.get('caja_compensacion_id', '')
        colaborador.fecha_ingreso = string_to_date(datos.get('fecha_ingreso', ''))
        colaborador.fecha_examen = string_to_date(datos.get('fecha_examen', ''))
        colaborador.fecha_dotacion = string_to_date(datos.get('fecha_dotacion', ''))
        colaborador.salario = datos.get('salario', '')
        colaborador.jefe_inmediato_id = datos.get('jefe_inmediato_id', '')
        colaborador.contrato_id = datos.get('contrato_id', '')
        colaborador.cargo_id = datos.get('cargo_id', '')
        colaborador.proceso_id = datos.get('proceso_id', '')
        colaborador.tipo_contrato_id = datos.get('tipo_contrato_id', '')
        colaborador.lugar_nacimiento_id = datos.get('centro_poblado_id', '')
        colaborador.rango_id = datos.get('rango_id', '')
        colaborador.usuario.email = datos.get('correo', '')
        colaborador.fecha_nacimiento = string_to_date(datos.get('fecha_nacimiento', ''))
        colaborador.usuario.first_name = datos.get('nombre', '')
        colaborador.usuario.last_name = datos.get('apellido', '')
        colaborador.identificacion = datos.get('identificacion', '')
        colaborador.tipo_identificacion_id = datos.get('tipo_identificacion_id', '')

        return colaborador
