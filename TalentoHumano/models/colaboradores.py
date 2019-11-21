from django.contrib.auth.models import User
from django.db import models
import random


from Administracion.models import Persona, Cargo, Proceso, TipoContrato, CentroPoblado, Rango
from EVA.General.conversiones import string_to_date
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from Proyectos.models import Contrato
from TalentoHumano.models import EntidadesCAFE


class Colaboradores (Persona, ModelDjangoExtensiones):
    objects = ManagerGeneral(campo_texto='jefe_inmediato')
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
    jefe_inmediato = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Jefe inmediato', null=True)
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

        usuario_creado = Colaboradores.crear_usuario(datos.get('nombre', ''), datos.get('apellido', ''),
                                                     datos.get('correo', ''))
        colaborador = Colaboradores()
        colaborador.usuario= usuario_creado
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
        colaborador.jefe_inmediato_id = datos.get('jefe_inmediato_id', None)
        if colaborador.jefe_inmediato_id == '':
            colaborador.jefe_inmediato_id = None

        colaborador.contrato_id = datos.get('contrato_id', '')
        colaborador.cargo_id = datos.get('cargo_id', '')
        colaborador.proceso_id = datos.get('proceso_id', '')
        colaborador.tipo_contrato_id = datos.get('tipo_contrato_id', '')
        colaborador.lugar_nacimiento_id = datos.get('centro_poblado_id', '')
        colaborador.rango_id = datos.get('rango_id', '')
        colaborador.fecha_nacimiento = string_to_date(datos.get('fecha_nacimiento', ''))
        colaborador.identificacion = datos.get('identificacion', '')
        colaborador.tipo_identificacion_id = datos.get('tipo_identificacion_id', '')
        colaborador.fecha_expedicion = string_to_date(datos.get('fecha_expedicion', ''))
        colaborador.genero = datos.get('genero', '')
        colaborador.telefono = datos.get('telefono', '')
        colaborador.estado = datos.get('estado', 'False') == 'True'
        return colaborador

    @staticmethod
    def crear_usuario(nombre: str, apellido: str, correo: str) -> User:

        usuario = User()
        usuario.first_name = nombre
        usuario.last_name = apellido
        usuario.email = correo
        nombre_1 = nombre.lower().split()
        apellido_1 = apellido.lower().split()
        usuario.username = nombre_1[0] + '.' + apellido_1[0]
        usuario_n = usuario.username
        while True:

            if User.objects.filter(username=usuario_n).exists():
                num = range(1, 99)
                r_num = random.choice(num)
                usuario_n = usuario.username + str(r_num)

            else:
                usuario.username = usuario_n
                return usuario
