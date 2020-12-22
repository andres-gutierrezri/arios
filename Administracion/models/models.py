import json

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, F, Value, CharField
from django.db.models.functions import Concat

from Administracion.models import Municipio
from EVA import settings
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


class Empresa(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    nit = models.TextField(max_length=20, verbose_name='NIT', null=False, blank=False, unique=True)
    digito_verificacion = models.SmallIntegerField(verbose_name='Digito de Verificación', null=True, blank=True)
    logo = models.ImageField(upload_to=f'{settings.EVA_PUBLIC_MEDIA}/logos-empresas', verbose_name='Logo', null=False,
                             blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    subempresa = models.BooleanField(verbose_name='Subempresa', null=False, blank=False)
    empresa_ppal = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Empresa Ppal', null=True,
                                     blank=False)
    tipo_persona = models.SmallIntegerField(verbose_name='Tipo de Persona', null=False, blank=False, default=1)
    matricula_mercantil = models.CharField(max_length=20, verbose_name='Matricula Mercantil', null=True, blank=True)
    responsabilidades_fiscales = models.CharField(max_length=200, verbose_name='Responsabilidades Fiscales', null=True,
                                                  blank=True)
    regimen_fiscal = models.SmallIntegerField(verbose_name='Régimen Fiscal', null=False, blank=False, default=48)
    tributos = models.CharField(max_length=10, verbose_name='Tributo', null=True, blank=True)
    codigo_postal = models.CharField(max_length=10, verbose_name='Código Postal', null=True, blank=True)
    direccion = models.CharField(max_length=300, verbose_name='Dirección', null=True, blank=True)
    municipio = models.ForeignKey(Municipio, verbose_name='Municipio', null=False, blank=False,
                                  on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def to_dict(self, campos=None, excluir=None):
        if excluir:
            excluir_cp = excluir.copy()
            excluir_cp.append('logo')
        else:
            excluir_cp = None
        emp_dict = super().to_dict(excluir=excluir_cp)

        if excluir is None or (excluir is not None and 'logo' not in excluir):
            emp_dict['logo'] = self.logo.url

        if not self.empresa_ppal_id and (campos is None or (campos is not None and 'empresa_ppal' in campos))\
                and (excluir is None or (excluir is not None and 'empresa_ppal' not in excluir)):
            emp_dict['empresa_ppal'] = 0
        return emp_dict

    @staticmethod
    def get_default():
        return Empresa(nombre='Empresa Default',
                       nit='',
                       logo='',
                       estado=False,
                       subempresa=False,
                       empresa_ppal=None,
                       id=0)

    @staticmethod
    def from_dictionary(datos: dict) -> 'Empresa':
        """
        Crea una instancia de Empresas con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear Empresas.
        :return: Instacia de entidad empresas con la información especificada en el diccionario.
        """
        empresa = Empresa()
        empresa.nombre = datos.get('nombre', '')
        empresa.nit = datos.get('nit', '')
        empresa.logo = datos.get('logo', None)
        empresa.estado = datos.get('estado', '') == 'True'
        empresa.subempresa = datos.get('subempresa', 'False') == 'True'
        empresa.empresa_ppal_id = datos.get('empresa_ppal_id', '')
        empresa.municipio_id = datos.get('municipio_id', '')
        empresa.direccion = datos.get('direccion', '')
        empresa.digito_verificacion = datos.get('digito_verificacion')
        empresa.tipo_persona = datos.get('tipo_persona')
        empresa.regimen_fiscal = datos.get('regimen_fiscal')
        responsabilidades = datos.getlist('responsabilidades')
        empresa.responsabilidades_fiscales = ';'.join(responsabilidades) if responsabilidades else ''
        empresa.tributos = datos.get('tributo')
        empresa.codigo_postal = datos.get('codigo_postal')
        empresa.matricula_mercantil = datos.get('matricula_mercantil', '')

        return empresa


class Cargo(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa',
                                null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'


class Proceso(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    sigla = models.CharField(max_length=5, verbose_name='Sigla', null=False, blank=False, default='')
    objeto = models.CharField(max_length=100, verbose_name='Objeto', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'


class Rango(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa',
                                null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Rango'
        verbose_name_plural = 'Rangos'


class TipoIdentificacionManager(ManagerGeneral):
    def get_xa_select_personas_activos(self) -> json:
        return self.get_x_estado(True, True).exclude(sigla="NIT")

    def get_activos_like_json(self):
        datos = []
        for elemento in self.get_x_estado(True, False):
            tipo_nit = True if elemento.sigla == 'NIT' else False
            datos.append({'id': elemento.id, 'tipo_nit': tipo_nit})
        return json.dumps(datos)


class TipoIdentificacion(models.Model):
    objects = TipoIdentificacionManager()
    
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    sigla = models.TextField(max_length=5, verbose_name='Sigla', null=False, blank=False, unique=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Identificación'
        verbose_name_plural = 'Tipos de Identificaciones'


class TipoContratoManager(ManagerGeneral):
    def tipos_laborares(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(laboral=True)

    def tipos_comerciales(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(laboral=False)


class TipoContrato(models.Model):
    objects = TipoContratoManager()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    laboral = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    sigla = models.CharField(max_length=5, verbose_name='Sigla', null=False, blank=False, default='')
    tiene_fecha_fin = models.BooleanField(verbose_name='Tiene Fecha de Finalización', null=False, blank=False,
                                          default=True)
    porcentaje_aiu = models.BooleanField(verbose_name='Porcentaje AIU', blank=False, null=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Contrato'
        verbose_name_plural = 'Tipos de Contratos'


class Persona(models.Model):

    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False,
                                      unique=True)
    fecha_expedicion = models.DateTimeField(verbose_name='Fecha de Expedición', null=False,
                                            blank=False)
    fecha_nacimiento = models.DateTimeField(verbose_name='Fecha de Nacimiento', null=True,
                                            blank=False)
    telefono = models.CharField(max_length=20, verbose_name='Teléfono', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)
    genero = models.CharField(max_length=1, verbose_name='Género', null=False, blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                            verbose_name='Tipo de identificación', null=True, blank=False)
    usuario = models.OneToOneField(User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=True,
                                   blank=False, related_name='%(app_label)s_%(class)s_usuario')
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=True,
                                     blank=True, related_name='%(app_label)s_%(class)s_usuario_crea')
    usuario_actualiza = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Actualiza",
                                          null=True, blank=True,
                                          related_name='%(app_label)s_%(class)s_usuario_actualiza')

    def __str__(self):
        return '{0} - {1}'.format(self.identificacion, self.nombre_completo)

    class Meta:
        abstract = True

    @property
    def nombres(self):
        return self.usuario.first_name if self.usuario else 'Sin nombres'

    @property
    def apellidos(self):
        return self.usuario.last_name if self.usuario else 'Sin apellidos'

    @property
    def nombre_completo(self):
        return '{0} {1}'.format(self.usuario.first_name, self.usuario.last_name) if self.usuario else 'Sin nombre'

    @property
    def primer_nombre_apellido(self):
        return '{0} {1}'.format(self.usuario.first_name.split(' ')[0], self.usuario.last_name.split(' ')[0]) \
            if self.usuario else 'Sin nombre'


class ImpuestoManager(ManagerGeneral):
    def get_xa_select_porcentaje(self) -> QuerySet:

        return super().get_queryset().filter(estado=True).values(campo_texto=F(self.campo_texto))\
            .annotate(campo_valor=Concat(Value('{"id":'), 'id', Value(', "porcentaje":'), 'porcentaje', Value('}'),
                                         output_field=CharField())) \
            .order_by(self.campo_texto)


class Impuesto(models.Model, ModelDjangoExtensiones):
    objects = ImpuestoManager()
    nombre = models.CharField(verbose_name="Nombre", max_length=50, null=False, blank=False)
    porcentaje = models.DecimalField(verbose_name='Porcentaje', decimal_places=2, max_digits=5, null=False)
    aplica_item = models.BooleanField(verbose_name='Aplica a Item', null=False)
    aplica_global = models.BooleanField(verbose_name='Aplica Global', null=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, default=True)
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateField(verbose_name='Fecha de Modificación', null=True, blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='ImpuestoCrea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=False, related_name='ImpuestoModifica')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Impuesto'
        verbose_name_plural = 'Impuestos'


class SubtipoProductoServicioManger(ManagerGeneral):
    def get_subtipo_productos_like_json(self):
        datos = []
        for elemento in self.get_x_estado(True, False).filter(es_servicio=False):
            datos.append({'id': elemento.id, 'nombre': elemento.nombre})
        return json.dumps(datos)

    def get_subtipo_servicios_like_json(self):
        datos = []
        for elemento in self.get_x_estado(True, False).filter(es_servicio=True):
            datos.append({'id': elemento.id, 'nombre': elemento.nombre})
        return json.dumps(datos)


class SubtipoProductoServicio(models.Model, ModelDjangoExtensiones):
    objects = SubtipoProductoServicioManger()
    nombre = models.CharField(verbose_name="Nombre", max_length=100, null=False, blank=False)
    descripcion = models.CharField(verbose_name="Descripción", max_length=300, null=False, blank=False)
    es_servicio = models.BooleanField(verbose_name="Es Servicio", null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Subtipo Producto Servicio'
        verbose_name_plural = 'Subtipos Productos Servicios'


class UnidadMedida(models.Model):
    objects = ManagerGeneral()

    id = models.CharField(max_length=4, verbose_name="Id", primary_key=True, null=False, blank=False)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    sigla = models.CharField(max_length=5, verbose_name='Sigla', null=False, blank=False, unique=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    admite_decimales = models.BooleanField(verbose_name='Admite Decimales', null=False, blank=False, default=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'


class ProductoServicio(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name="Nombre", max_length=100, null=False, blank=False)
    descripcion = models.CharField(verbose_name="Descripción", max_length=300, null=False, blank=False)
    subtipo_producto_servicio = models.ForeignKey(SubtipoProductoServicio, on_delete=models.DO_NOTHING, null=False,
                                                  verbose_name="Subtipo de Producto o Servicio", blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Producto y Servicio'
        verbose_name_plural = 'Productos y Servicios'

