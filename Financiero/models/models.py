import json
from typing import List

from django.db import models

from Administracion.models import Tercero
from EVA import settings
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


class EntidadBancariaManger(ManagerGeneral):
    def get_like_json(self):
        datos = []
        for elemento in self.get_x_estado(True, False):
            datos.append({'id': elemento.id, 'nombre': elemento.nombre})
        return json.dumps(datos)


class EntidadBancaria(models.Model):
    objects = EntidadBancariaManger()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)
    codigo_banco = models.CharField(verbose_name='Código del Banco', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Entidad Bancaria'
        verbose_name_plural = 'Entidades Bancarias'


class ActividadEconomicaManger(ManagerGeneral):
    def get_xa_select_actividades_con_codigo(self) -> List:
        datos = []
        for obj in super().get_queryset():
            datos.append({'campo_valor': obj.id, 'campo_texto': obj})
        return datos


class ActividadEconomica(models.Model):
    objects = ActividadEconomicaManger()
    nombre = models.CharField(verbose_name='Nombre', max_length=200, null=False, blank=False)
    codigo_ciiu = models.CharField(verbose_name='Código CIIU', max_length=10, null=False, blank=False)

    def __str__(self):
        return '{0} - {1}'.format(self.codigo_ciiu, self.nombre)

    class Meta:
        verbose_name = 'Actividad Económica'
        verbose_name_plural = 'Actividades Económicas'


class ProveedorActividadEconomica(models.Model, ModelDjangoExtensiones):
    actividad_principal = models.ForeignKey(ActividadEconomica, on_delete=models.DO_NOTHING, null=False, blank=False,
                                            verbose_name='Actividad Principal',
                                            related_name='proveedor_actividad_principal')
    actividad_secundaria = models.ForeignKey(ActividadEconomica, on_delete=models.DO_NOTHING, null=True, blank=True,
                                             verbose_name='Actividad Secundiaria',
                                             related_name='proveedor_actividad_secundaria')
    otra_actividad = models.ForeignKey(ActividadEconomica, on_delete=models.DO_NOTHING, null=True, blank=True,
                                       verbose_name='Otra Actividad', related_name='proveedor_otra_atividad')
    tipo_contribuyente = models.SmallIntegerField(verbose_name='Tipo Contribuyente', null=False, blank=False)
    numero_resolucion = models.CharField(verbose_name='Número de Resolución', max_length=100, null=True, blank=True)
    contribuyente_iyc = models.CharField(verbose_name='Contribuyente de Industria y Comercio', max_length=100,
                                         null=True, blank=True)
    entidad_publica = models.CharField(verbose_name='Número de Resolución', max_length=100, null=True, blank=True)
    proveedor = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Usuario',
                                  null=False, blank=False)
    declara_renta = models.BooleanField(verbose_name='Declara Renta', null=True, blank=False)

    def __str__(self):
        return 'Información de la Actividad Económica del usuario {0}'.format(self.proveedor.usuario.get_full_name())

    class Meta:
        verbose_name = 'Actividad Económica del Proveedor'
        verbose_name_plural = 'Actividades Económicas de Los Proveedores'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ProveedorActividadEconomica':
        """
        Crea una instancia de Proveedor Actividad Económica con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el registro de Proveedor Actividad Económica.
        :return: Instacia de entidad Proveedor Actividad Económica con la información especificada en el diccionario.
        """
        proveedor_ae = ProveedorActividadEconomica()
        proveedor_ae.actividad_principal_id = datos.get('actividad_principal', '')
        proveedor_ae.actividad_secundaria_id = datos.get('actividad_secundaria', '')
        proveedor_ae.otra_actividad_id = datos.get('otra_actividad', '')
        proveedor_ae.tipo_contribuyente = datos.get('tipo_contribuyente', 0)
        proveedor_ae.numero_resolucion = datos.get('resolucion', '')
        proveedor_ae.contribuyente_iyc = datos.get('contribuyente_iyc', '')
        proveedor_ae.entidad_publica = datos.get('entidad_publica', '')
        proveedor_ae.declara_renta = datos.get('declara_renta', 'False') == 'on'

        return proveedor_ae


def custom_upload_to(instance, filename):
    return '{2}/Proveedores/CertificacionesBancarias/{0}/{1}'\
        .format(instance.tercero.identificacion, filename, settings.EVA_PRIVATE_MEDIA)


class EntidadBancariaTercero(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', blank=False, null=False)
    entidad_bancaria = models.ForeignKey(EntidadBancaria, on_delete=models.DO_NOTHING, verbose_name='Entidad Bancaria',
                                         null=False, blank=False)
    tipo_cuenta = models.SmallIntegerField(verbose_name='Tipo de Cuenta', null=False, blank=False, default=1)
    numero_cuenta = models.CharField(max_length=50, verbose_name='Número de Cuenta', null=False, blank=False)
    certificacion = models.FileField(upload_to=custom_upload_to, blank=False, null=False)

    def __str__(self):
        return 'Entidad Bancaria de {0}'.format(self.tercero)

    class Meta:
        verbose_name = 'Entidad Bancaria del Tercero'
        verbose_name_plural = 'Entidades Bancarias de los Terceros'

    @staticmethod
    def from_dictionary(datos: dict) -> 'EntidadBancariaTercero':
        """
        Crea una instancia de Entidad Bancaria Tercero con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el registro de Entidad Bancaria Tercero.
        :return: Instacia de entidad Entidad Bancaria Tercero con la información especificada en el diccionario.
        """
        entidad_tercero = EntidadBancariaTercero()
        entidad_tercero.tipo_cuenta = datos.get('tipo_cuenta', '')
        entidad_tercero.entidad_bancaria_id = datos.get('entidad_bancaria', '')

        return entidad_tercero
