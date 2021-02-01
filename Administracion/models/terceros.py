import json
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.http import QueryDict

from EVA import settings
from EVA.General.modelmanagers import ManagerGeneral
from .models import Empresa, TipoIdentificacion, Persona, SubproductoSubservicio
from .divipol import CentroPoblado, Municipio
from EVA.General.modeljson import ModelDjangoExtensiones
from Administracion.enumeraciones import TipoPersona, EstadosProveedor


class TipoTercero(models.Model):
    objects = ManagerGeneral()

    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Tercero'
        verbose_name_plural = 'Tipos de Terceros'

    # Tipos Fijos
    CLIENTE = 1
    PROVEEDOR = 2
    SUPERVISOR = 3
    INTERVENTOR = 4


class TerceroManger(ManagerGeneral):

    def clientes(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_tercero_id=TipoTercero.CLIENTE)

    def clientes_xa_select(self):
        return self.clientes(True, True)

    def proveedores(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(tipo_tercero_id=TipoTercero.PROVEEDOR)

    def proveedores_xa_select(self):
        return self.proveedores(True, True)


class Tercero(models.Model, ModelDjangoExtensiones):
    objects = TerceroManger()

    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=True, blank=False)
    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False)
    digito_verificacion = models.SmallIntegerField(verbose_name='Digito de Verificación', null=True, blank=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING, null=True, blank=False,
                                            verbose_name='Tipo de identificación',
                                            related_name='tercero_tipo_identificacion')
    ciudad = models.ForeignKey(Municipio, on_delete=models.DO_NOTHING, verbose_name='Ciudad', null=True, blank=True,
                               related_name='proveedor_ciudad')
    centro_poblado = models.ForeignKey(CentroPoblado, on_delete=models.DO_NOTHING,
                                       verbose_name='Centro poblado', null=True, blank=False)
    tipo_tercero = models.ForeignKey(TipoTercero, on_delete=models.DO_NOTHING, verbose_name='Tipo Tercero', null=True,
                                     blank=False)
    direccion = models.CharField(max_length=100, verbose_name='Dirección', null=True, blank=False)
    telefono = models.CharField(max_length=30, verbose_name='Teléfono', null=True, blank=False)
    fax = models.CharField(max_length=30, verbose_name='fax', null=True, blank=True)
    tipo_persona = models.SmallIntegerField(verbose_name='Tipo de Persona', null=False, blank=False, default=1)
    responsabilidades_fiscales = models.CharField(max_length=200, verbose_name='Responsabilidades Fiscales', null=True,
                                                  blank=True)
    regimen_fiscal = models.SmallIntegerField(verbose_name='Régimen Fiscal', null=True, blank=True)
    tributos = models.CharField(max_length=10, verbose_name='Tributo', null=True, blank=True)
    correo_facelec = models.EmailField(max_length=254, verbose_name='Correo Facturación Electrónica', null=True,
                                       blank=True)
    codigo_postal = models.CharField(max_length=6, verbose_name='Código Postal', null=True, blank=True)
    telefono_fijo_principal = models.CharField(max_length=30, verbose_name='Teléfono Fijo Principal',
                                               null=True, blank=True)
    telefono_fijo_auxiliar = models.CharField(max_length=30, verbose_name='Teléfono Fijo auxiliar',
                                              null=True, blank=True)
    telefono_movil_principal = models.CharField(max_length=30, verbose_name='Teléfono Movil Principal',
                                                null=True, blank=True)
    telefono_movil_auxiliar = models.CharField(max_length=30, verbose_name='Teléfono Movil Auxiliar',
                                               null=True, blank=True)
    correo_principal = models.CharField(max_length=254, verbose_name='Correo Principal', null=True, blank=True)
    correo_auxiliar = models.CharField(max_length=254, verbose_name='Correo Auxiliar', null=True, blank=True)
    nombre_rl = models.CharField(max_length=100, verbose_name='Nombre del Representante Legal', null=True, blank=True)
    tipo_identificacion_rl = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                               verbose_name='Tipo de identificación del Representante Legal',
                                               null=True, blank=True, related_name='proveedor_rl_tipo_identificacion')
    identificacion_rl = models.CharField(max_length=100, verbose_name='Identificación del Representante Legal',
                                         null=True, blank=True)
    lugar_expedicion_rl = models.ForeignKey(Municipio, on_delete=models.DO_NOTHING, null=True, blank=True,
                                            related_name='proveedor_rl_lugar_expedicion',
                                            verbose_name='Lugar de Expedicion del Id del RL')
    fecha_constitucion = models.DateTimeField(verbose_name='Fecha de Constitución', null=True, blank=True)
    fecha_inicio_actividad = models.DateTimeField(verbose_name='Fecha de Inicio de Actividad', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario', null=True, blank=True)
    estado_proveedor = models.SmallIntegerField(choices=EstadosProveedor.choices, verbose_name='Estado del Proveedor',
                                                null=True, blank=True)
    modificaciones = models.TextField(verbose_name='Modificaciones', null=True, blank=True)
    bienes_servicios = models.TextField(verbose_name='Bienes y Servicios que Ofrece', null=True, blank=True)
    es_vigente = models.BooleanField(verbose_name='Es Vigente', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tercero'
        verbose_name_plural = 'Terceros'
        permissions = [("view_proveedor", "Can view proveedor"),
                       ("manage_proveedor", "Can manage proveedor")]

    def empresa_to_dict(self):
        if self.empresa:
            return self.empresa.to_dict()
        else:
            return Empresa.get_default().to_dict()

    @staticmethod
    def from_dictionary(datos: QueryDict) -> 'Tercero':
        """
        Crea una instancia de Tercero con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el tercero.
        :return: Instacia de tercero con la información especificada en el diccionario.
        """
        tercero = Tercero()
        tercero.nombre = datos.get('nombre', '')
        tercero.identificacion = datos.get('identificacion', '')
        tercero.tipo_identificacion_id = datos.get('tipo_identificacion_id', '')
        tercero.estado = datos.get('estado', 'False') == 'True'
        tercero.empresa_id = datos.get('empresa', '')
        tercero.fecha_modificacion = datetime.now()
        tercero.tipo_tercero_id = datos.get('tipo_tercero_id', '')
        tercero.centro_poblado_id = datos.get('centro_poblado_id', '')
        tercero.telefono = datos.get('telefono', '')
        tercero.fax = datos.get('fax', '')
        tercero.direccion = datos.get('direccion', '')
        tercero.digito_verificacion = datos.get('digito_verificacion')
        tercero.es_vigente = True
        if int(tercero.tipo_tercero_id) == TipoTercero.CLIENTE:
            tercero.tipo_persona = datos.get('tipo_persona')
            tercero.regimen_fiscal = datos.get('regimen_fiscal')
            responsabilidades = datos.getlist('responsabilidades')
            tercero.responsabilidades_fiscales = ';'.join(responsabilidades) if responsabilidades else ''
            tercero.tributos = datos.get('tributo')
            tercero.correo_facelec = datos.get('correo')
            tercero.codigo_postal = datos.get('codigo_postal')
        else:
            tercero.tipo_persona = TipoPersona.JURIDICA
        return tercero


class UsuarioTercero(Persona):
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', null=False, blank=False)

    def __str__(self):
        return '{0} {1}'.format(self.usuario.first_name, self.usuario.last_name)

    class Meta:
        verbose_name = 'Usuario Tercero'
        verbose_name_plural = 'Usuarios Terceros'


def get_xa_select_con_opcionales(datos):
    opciones = []
    for d in datos:
        if d.obligatorio:
            opciones.append({'campo_valor': d.id, 'campo_texto': d.nombre})
        else:
            opciones.append({'campo_valor': d.id, 'campo_texto': '{0} (Opcional)'.format(d.nombre)})
    return opciones


class TipoDocumentoTerceroManager(ManagerGeneral):
    def get_xa_select_activos_aplica_natural(self) -> QuerySet:
        return self.get_xa_select_activos().filter(aplica_natural=True)

    def get_xa_select_activos_aplica_juridica(self) -> QuerySet:
        return self.get_xa_select_activos().filter(aplica_juridica=True)

    def get_xa_select_con_opcionales_aplica_natural(self):
        return get_xa_select_con_opcionales(self.filter(aplica_natural=True))

    def get_xa_select_con_opcionales_aplica_juridica(self):
        return get_xa_select_con_opcionales(self.filter(aplica_juridica=True))


class TipoDocumentoTercero(models.Model):
    objects = TipoDocumentoTerceroManager()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)
    aplica_natural = models.BooleanField(verbose_name='Aplica Natural', null=False, blank=False)
    aplica_juridica = models.BooleanField(verbose_name='Aplica Jurídica', null=False, blank=False)
    obligatorio = models.BooleanField(verbose_name='Obligatorio', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Documento Tercero'
        verbose_name_plural = 'Tipos de Documentos Terceros'


def custom_upload_to(instance, filename):
    return '{2}/Proveedores/Documentos/{0}/{1}'\
        .format(instance.tercero.identificacion, filename, settings.EVA_PRIVATE_MEDIA)


class DocumentoTercero(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    documento = models.FileField(upload_to=custom_upload_to, verbose_name='Documento', null=False, blank=False)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=True, blank=True)
    tipo_documento = models.ForeignKey(TipoDocumentoTercero, on_delete=models.DO_NOTHING, blank=False, null=True)
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', blank=False, null=False)
    fecha_crea = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', blank=False, null=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)

    def __str__(self):
        return '{0}-{1}'.format(self.tipo_documento, self.tercero)

    class Meta:
        verbose_name = 'Documento Tercero'
        verbose_name_plural = 'Documentos Terceros'
        unique_together = ('tipo_documento', 'tercero')


class Certificacion(models.Model):
    objects = ManagerGeneral()
    tercero = models.ForeignKey(Tercero, on_delete=models.CASCADE, verbose_name='Tercero', blank=False, null=False)
    fecha_crea = models.DateTimeField(verbose_name='Fecha de Creación', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)

    def __str__(self):
        return 'Certificación de {0}'.format(self.tercero)

    class Meta:
        verbose_name = 'Certificación'
        verbose_name_plural = 'Certifiacaiones'


class ProveedorProductoServicioManger(ManagerGeneral):
    def get_activos_like_json(self):
        datos = []
        for elemento in self.get_x_estado(True, False):
            if elemento.subproducto_subservicio.producto_servicio.es_servicio:
                tipo_producto_servicio = 2
            else:
                tipo_producto_servicio = 1
            datos.append({'tipo_producto_servicio': tipo_producto_servicio,
                          'producto_servicio': elemento.subproducto_subservicio.producto_servicio_id,
                          'subproducto_subservicio': elemento.subproducto_subservicio_id})
        return json.dumps(datos)


class ProveedorProductoServicio(models.Model, ModelDjangoExtensiones):
    objects = ProveedorProductoServicioManger()
    subproducto_subservicio = models.ForeignKey(SubproductoSubservicio, on_delete=models.DO_NOTHING,
                                                verbose_name="Subproducto o Subservicio", null=False, blank=False)
    proveedor = models.ForeignKey(Tercero, on_delete=models.CASCADE,
                                  verbose_name="Proveedor", null=False, blank=False)

    def __str__(self):
        return '{0}-{1}'.format(self.proveedor, self.subproducto_subservicio)

    class Meta:
        verbose_name = 'Proveedor Producto o Servicio'
        verbose_name_plural = 'Proveedores Productos o Servicios'


class SolicitudProveedor(models.Model):
    proveedor = models.ForeignKey(Tercero, on_delete=models.CASCADE,
                                  verbose_name="Proveedor", null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', blank=False, null=False)
    comentarios = models.CharField(max_length=300, verbose_name='Comentarios', blank=False, null=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False)
    aprobado = models.BooleanField(verbose_name='Aprobado', blank=False, null=False)

    def __str__(self):
        return '{0}'.format(self.proveedor)

    class Meta:
        verbose_name = 'Solicitud Proveedor'
        verbose_name_plural = 'Solicitudes Proveedores'
