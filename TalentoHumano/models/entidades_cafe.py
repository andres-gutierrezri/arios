from django.db import models
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from django.db.models import QuerySet


class TipoEntidadesCAFE(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de entidad'
        verbose_name_plural = 'Tipos de entidades'

    # Tipos Fijos
    TODAS = 0
    ARL = 1
    EPS = 2
    CAJA_COMPENSACION = 3
    AFP = 4


class EntidadesManger(ManagerGeneral):

    def arl(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_entidad_id=TipoEntidadesCAFE.ARL)

    def arl_xa_select(self):
        return self.arl(True, True)

    def eps(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_entidad_id=TipoEntidadesCAFE.EPS)

    def eps_xa_select(self):
        return self.eps(True, True)

    def caja_compensacion(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_entidad_id=TipoEntidadesCAFE.CAJA_COMPENSACION)

    def caja_compensacion_xa_select(self):
        return self.caja_compensacion(True, True)

    def afp(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_entidad_id=TipoEntidadesCAFE.AFP)

    def afp_xa_select(self):
        return self.afp(True, True)


class EntidadesCAFE(models.Model, ModelDjangoExtensiones):
    objects = EntidadesManger()
    tipo_entidad = models.ForeignKey(TipoEntidadesCAFE, on_delete=models.DO_NOTHING, verbose_name='Tipo de entidad',
                                     null=True, blank=False)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    direccion = models.CharField(max_length=100, verbose_name='Dirección', null=False, blank=False)
    nombre_contacto = models.CharField(max_length=100, verbose_name='Nombre de contacto', null=False, blank=False)
    telefono_contacto = models.CharField(max_length=30, verbose_name='Teléfono de contacto', null=False, blank=False)
    correo = models.EmailField(max_length=100, verbose_name='Correo del supervisor', null=False, blank=False,
                               error_messages={'invalid': "Ingrese una dirección de correo válida"})
    direccion_web = models.CharField(max_length=100, verbose_name='Dirección web', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'

    @staticmethod
    def from_dictionary(datos: dict) -> 'EntidadesCAFE':
        """
        Crea una instancia de EntidadesCAFE con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear la EntidadCAFE.
        :return: Instacia de entidad cafe con la información especificada en el diccionario.
        """
        entidad_cafe = EntidadesCAFE()
        entidad_cafe.tipo_entidad_id = datos.get('tipo_entidad_id', '')
        entidad_cafe.nombre = datos.get('nombre', '')
        entidad_cafe.direccion = datos.get('direccion', '')
        entidad_cafe.nombre_contacto = datos.get('nombre_contacto', '')
        entidad_cafe.telefono_contacto = datos.get('telefono_contacto', '')
        entidad_cafe.correo = datos.get('correo', '')
        entidad_cafe.direccion_web = datos.get('direccion_web', '')

        return entidad_cafe



