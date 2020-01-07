from django.contrib.auth.models import User
from django.db import models
import random
import unicodedata
from django.db.models import F, QuerySet, CharField, Value
from django.db.models.functions import Concat

from Administracion.models import Persona, Cargo, Proceso, TipoContrato, CentroPoblado, Rango, Empresa
from EVA.General.conversiones import string_to_date
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from Proyectos.models import Contrato
from TalentoHumano.models import EntidadesCAFE


class ColaboradorManger(ManagerGeneral):

    def get_x_estado(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        filtro = {}

        if estado is not None and 'estado' in self.model._meta._forward_fields_map:
            filtro['estado'] = estado
        if xa_select:
            return super().get_queryset().filter(**filtro).\
                values(campo_valor=F('id')).annotate(campo_texto=Concat('usuario__first_name', Value(' '),
                                                                        'usuario__last_name',
                                                                        output_field=CharField()))\
                .order_by('usuario__first_name', 'usuario__last_name')
        else:
            return super().get_queryset().filter(**filtro)


class Colaborador(Persona, ModelDjangoExtensiones):
    objects = ColaboradorManger()
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
    fecha_dotacion = models.DateField(verbose_name='Fecha de dotación', null=True, blank=False)
    salario = models.IntegerField(verbose_name="Salario", null=True, blank=False)
    jefe_inmediato = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Jefe inmediato', null=True,
                                       blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING, verbose_name='Cargo', null=False, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=False, blank=False)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.DO_NOTHING, verbose_name='Tipo de contrato',
                                      null=False, blank=False)
    lugar_nacimiento = models.ForeignKey(CentroPoblado, on_delete=models.DO_NOTHING, verbose_name='Lugar de nacimiento',
                                         null=False, blank=False)
    rango = models.ForeignKey(Rango, on_delete=models.DO_NOTHING, verbose_name='Rango', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    foto_perfil = models.ImageField(upload_to='foto_perfil', blank=True, default='foto_perfil/profile-none.png')
    empresa_sesion = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa Sesion',
                                       null=True, blank=False)
    grupo_sanguineo = models.CharField(max_length=3, verbose_name="Grupo sanguíneo", null=False, blank=False)
    nombre_contacto = models.CharField(max_length=100, verbose_name='Nombre del contacto', null=False, blank=False)
    parentesco = models.CharField(max_length=100, verbose_name='Parentesco', null=False, blank=False)
    telefono_contacto = models.CharField(max_length=20, verbose_name='Teléfono del contacto', null=False, blank=False)

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'

    def to_json(self, campos=None, excluir=None):
        campos = [{
            'foto_perfil': self.foto_perfil.url
        }]
        return campos

    def empresa_to_dict(self):
        if self.empresa_sesion:
            return self.empresa_sesion.to_dict()
        else:
            return Empresa.get_default().to_dict()

    @staticmethod
    def from_dictionary(datos: dict) -> 'Colaborador':
        """
        Crea una instancia de Colaboradores con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear Colaboradores.
        :return: Instacia de entidad colaboradores con la información especificada en el diccionario.
        """
        colaborador = Colaborador()
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
        if colaborador.jefe_inmediato_id == '':
            colaborador.jefe_inmediato_id = None
        colaborador.cargo_id = datos.get('cargo_id', '')
        colaborador.proceso_id = datos.get('proceso_id', '')
        colaborador.tipo_contrato_id = datos.get('tipo_contrato_id', '')
        colaborador.lugar_nacimiento_id = datos.get('centro_poblado_id', '')
        colaborador.rango_id = datos.get('rango_id', '')
        colaborador.fecha_nacimiento = string_to_date(datos.get('fecha_nacimiento', ''))
        colaborador.identificacion = datos.get('identificacion', '')
        colaborador.tipo_identificacion_id = datos.get('tipo_identificacion_id', '')
        colaborador.fecha_expedicion = string_to_date(datos.get('fecha_expedicion', ''))
        colaborador.genero = datos.get('genero', '')[0:1]
        colaborador.telefono = datos.get('telefono', '')
        colaborador.estado = datos.get('estado', 'True') == 'True'
        colaborador.foto_perfil = datos.get('foto_perfil', None)
        colaborador.usuario_id = datos.get('usuario_id', None)
        usuario_creado = Colaborador.crear_usuario(datos.get('nombre', ''), datos.get('apellido', ''),
                                                   datos.get('correo', ''),  colaborador.usuario_id)
        colaborador.usuario = usuario_creado
        colaborador.nombre_contacto = datos.get('nombre_contacto', '')
        colaborador.telefono_contacto = datos.get('telefono_contacto', '')
        colaborador.grupo_sanguineo = datos.get('grupo_sanguineo', '')
        colaborador.parentesco = datos.get('parentesco', '')
        return colaborador

    @staticmethod
    def crear_usuario(nombre: str, apellido: str, correo: str, usuario_id: int) -> User:

        usuario = User(id=usuario_id)
        usuario.first_name = nombre
        usuario.last_name = apellido
        usuario.email = correo
        nombre_1 = nombre.lower().split()
        apellido_1 = apellido.lower().split()
        nombre_1_n = unicodedata.normalize("NFKD", str(nombre_1[0])).encode("ascii", "ignore").decode("ascii")
        apellido_1_n = unicodedata.normalize("NFKD", str(apellido_1[0])).encode("ascii", "ignore").decode("ascii")
        usuario.username = nombre_1_n + '.' + apellido_1_n
        usuario_n = usuario.username.replace("[", "").replace("'", "").replace("]", "")

        while True:
            existe = User.objects.filter(username=usuario_n).exclude(id=usuario_id).exists() if usuario_id else User.\
                objects.filter(username=usuario_n).exists()

            if existe:
                num = range(1, 99)
                r_num = random.choice(num)
                usuario_n = usuario.username + str(r_num)

            else:
                usuario.username = usuario_n

                return usuario


class ColaboradorContratoManger(models.Manager):

    def get_ids_contratos(self, colaborador_id: int = None, colaborador: Colaborador = None) -> QuerySet:
        if colaborador:
            colaborador_id = colaborador.id

        filtro = {}
        if colaborador_id:
            filtro['colaborador_id'] = colaborador_id

        return super().get_queryset().filter(**filtro).values_list('contrato_id', flat=True)

    def get_ids_contratos_list(self, colaborador_id: int = None, colaborador: Colaborador = None) -> list:
        return list(self.get_ids_contratos(colaborador_id, colaborador))


class ColaboradorContrato(models.Model):
    objects = ColaboradorContratoManger()
    colaborador = models.ForeignKey(Colaborador, on_delete=models.DO_NOTHING, verbose_name='Colaborador', null=False,
                                    blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.DO_NOTHING, verbose_name='Contrato', null=False,
                                 blank=False)

    def __str__(self):
        return str(self.contrato.id)

    class Meta:
        unique_together = ('colaborador', 'contrato')

