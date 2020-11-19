from django.db import models

from EVA.General.modelmanagers import ManagerGeneral


class EntidadBancaria(models.Model):
    objects = ManagerGeneral()
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
    codigo_ciiu = models.CharField(verbose_name='Codigo CIIU', max_length=10, null=False, blank=False)

    def __str__(self):
        return '{0} - {1}'.format(self.codigo_ciiu, self.nombre)

    class Meta:
        verbose_name = 'Actividad Económica'
        verbose_name_plural = 'Actividades Económicas'


class TipoPersona(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Persona'
        verbose_name_plural = 'Tipos de Personas'


class TipoContribuyente(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Contribuyente'
        verbose_name_plural = 'Tipos de Contribuyentes'


class RegimenManager(ManagerGeneral):
    def get_activos_like_json(self):
        datos = []
        for elemento in self.get_x_estado(True, False):
            datos.append({'id': elemento.id, 'aplica_publica': elemento.aplica_publica})
        return json.dumps(datos)


class Regimen(models.Model):
    objects = RegimenManager()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)
    aplica_publica = models.BooleanField(verbose_name='Apica Entidad Pública', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Régimen'
        verbose_name_plural = 'Regímenes'


class ProveedorActividadEconomica(models.Model):
    actividad_principal = models.ForeignKey(ActividadEconomica, on_delete=models.DO_NOTHING, null=False, blank=False,
                                            verbose_name='Actividad Principal',
                                            related_name='proveedor_actividad_principal')
    actividad_secundaria = models.ForeignKey(ActividadEconomica, on_delete=models.DO_NOTHING, null=True, blank=True,
                                             verbose_name='Actividad Secundiaria',
                                             related_name='proveedor_actividad_secundaria')
    otra_actividad = models.ForeignKey(ActividadEconomica, on_delete=models.DO_NOTHING, null=True, blank=True,
                                       verbose_name='Otra Actividad', related_name='proveedor_otra_atividad')
    regimen = models.ForeignKey(Regimen, on_delete=models.DO_NOTHING, null=False, blank=False,
                                verbose_name='Régimen')
    tipo_contribuyente = models.ForeignKey(TipoContribuyente, on_delete=models.DO_NOTHING, null=False, blank=False,
                                           verbose_name='Tipo Contribuyente')
    numero_resolucion = models.CharField(verbose_name='Número de Resolución', max_length=100, null=True, blank=True)
    contribuyente_iyc = models.CharField(verbose_name='Contribuyente de Industria y Comercio', max_length=100,
                                         null=True, blank=True)
    entidad_publica = models.CharField(verbose_name='Número de Resolución', max_length=100, null=True, blank=True)
    proveedor = models.OneToOneField(Tercero, on_delete=models.DO_NOTHING, verbose_name='Usuario',
                                     null=False, blank=False)
    bienes_servicios = models.TextField(verbose_name='Bienes y Servicios que Ofrece', null=False, blank=False)

    def __str__(self):
        return 'Información de la Actividad Economica del usuario {0}'.format(self.proveedor.usuario.get_full_name())

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
        proveedor_ae.regimen_id = datos.get('regimen', '')
        proveedor_ae.tipo_contribuyente_id = datos.get('tipo_contribuyente', '')
        proveedor_ae.numero_resolucion = datos.get('resolucion', '')
        proveedor_ae.contribuyente_iyc = datos.get('contribuyente_iyc', '')
        proveedor_ae.entidad_publica = datos.get('entidad_publica', '')
        proveedor_ae.bienes_servicios = datos.get('bienes_servicios', '')

        return proveedor_ae
