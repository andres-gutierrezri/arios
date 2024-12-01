
from django.db import models
from datetime import datetime


from EVA import settings
from django.contrib.auth.models import User
# Create your models here.
from Administracion.models import Empresa, Proceso
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from SGI.Enumeraciones import MedioSoporte, TiempoConservacion


class GrupoDocumento(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)
    es_general = models.BooleanField(verbose_name='Es General', null=False, blank=False, default=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Grupo de documento'
        verbose_name_plural = 'Grupos de documentos'


class CadenaAprobacionEncabezado(models.Model):
    objects = ManagerGeneral()
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False, default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cadena de aprobación encabezado'
        verbose_name_plural = 'Cadenas de aprobaciones encabezados'

    @staticmethod
    def from_dictionary(datos: dict) -> 'CadenaAprobacionEncabezado':
        """
        Crea una instancia de Documento con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el docuemento.
        :return: Instacia de Documento con la información especificada en el diccionario.
        """
        cadena_aprobacion = CadenaAprobacionEncabezado()
        cadena_aprobacion.nombre = datos.get('nombre', '')
        cadena_aprobacion.fecha_creacion = datos.get('fecha_creacion', '')
        cadena_aprobacion.estado = datos.get('estado', 'False') == 'True'

        return cadena_aprobacion


class CadenaAprobacionDetalle(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario', null=True,
                                blank=False)
    orden = models.SmallIntegerField(verbose_name='Orden', null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de Aprobación', null=False, blank=False)

    def __str__(self):
        return self.usuario.first_name

    class Meta:
        verbose_name = 'Detalle de cadena de aprobación'
        verbose_name_plural = 'Detalles de cadenas de aprobaciones'


class Documento(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    codigo = models.CharField(max_length=20, verbose_name='Código', null=False, blank=False)
    medio_soporte = models.SmallIntegerField(choices=MedioSoporte.choices, verbose_name='Medio Soporte',
                                             null=False, blank=False)
    tiempo_conservacion = models.SmallIntegerField(choices=TiempoConservacion.choices,
                                                   verbose_name='Tiempo Conservación', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    version_actual = models.SmallIntegerField(verbose_name='Versión Actual', null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de aprobación', null=True, blank=False)
    grupo_documento = models.ForeignKey(GrupoDocumento, on_delete=models.DO_NOTHING,
                                        verbose_name='Grupo de documento', null=True, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False, default=True)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=True,
                                     blank=True, related_name='%(app_label)s_%(class)s_usuario_crea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=True, related_name='%(app_label)s_%(class)s_usuario_modifica')

    def __str__(self):
        return '{0} {1}'.format(self.codigo, self.nombre) +\
               (' v{}'.format(self.version_actual) if self.version_actual != 0 else '')

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'Documento':
        """
        Crea una instancia de Documento con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el docuemento.
        :return: Instacia de Documento con la información especificada en el diccionario.
        """
        documento = Documento()
        documento.nombre = datos.get('nombre', '')
        documento.codigo = datos.get('codigo', '')
        documento.fecha_modificacion = datetime.now()
        documento.version_actual = datos.get('version_actual', '')
        documento.cadena_aprobacion_id = datos.get('cadena_aprobacion_id', None)
        documento.grupo_documento_id = datos.get('grupo_documento_id', '')
        documento.proceso_id = datos.get('proceso_id', '')
        documento.medio_soporte = datos.get('soporte_id', None)
        documento.tiempo_conservacion = datos.get('conservacion_id', None)

        return documento

    @property
    def version_minima_siguiente(self):
        return self.version_actual + 1

    def ya_existe_codigo(self, editando=False):
        consulta = Documento.objects.filter(codigo__iexact=self.codigo, grupo_documento_id=self.grupo_documento_id,
                                            proceso_id=self.proceso_id, estado=True)
        if editando:
            consulta = consulta.exclude(id=self.id)

        return consulta.exists()

    def ya_existe_nombre(self, editando=False):
        consulta = Documento.objects.filter(nombre__iexact=self.nombre, grupo_documento_id=self.grupo_documento_id,
                                            proceso_id=self.proceso_id, estado=True)
        if editando:
            consulta = consulta.exclude(id=self.id)

        return consulta.exists()


class EstadoArchivo(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Estado de Archivo'
        verbose_name_plural = 'Estados de Archivos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'EstadoArchivo':
        """
        Crea una instancia de Archivo con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el docuemento.
        :return: Instacia de Documento con la información especificada en el diccionario.
        """
        estado = EstadoArchivo()
        estado.nombre = datos.get('nombre', '')
        estado.descripcion = datos.get('descripcion', '')

        return estado
    #Estados Fijos
    PENDIENTE = 0
    APROBADO = 1
    OBSOLETO = 2
    RECHAZADO = 3
    ELIMINADO = 4


def custom_upload_to(instance, filename):
    return '{6}/SGI/Documentos/{0:d}/{1:d}/{2} {3} v{4}.{5}'\
        .format(instance.documento.proceso.empresa.id, instance.documento.proceso.id, instance.documento.codigo,
                instance.documento.nombre, instance.version, filename.split(".")[-1], settings.EVA_PRIVATE_MEDIA)


class Archivo(models.Model):
    objects = ManagerGeneral()
    documento = models.ForeignKey(Documento, on_delete=models.DO_NOTHING, verbose_name='Documento', null=True,
                                  blank=False)
    version = models.SmallIntegerField(verbose_name='Versión', null=False, blank=False)
    notas = models.CharField(max_length=500, verbose_name='Notas', null=False, blank=False)
    fecha_documento = models.DateField(verbose_name='Fecha del Documento', null=False, blank=False)
    archivo = models.FileField(upload_to=custom_upload_to, blank=True, max_length=250)
    enlace = models.CharField(max_length=300, verbose_name='Enlace', null=True, blank=True)
    hash = models.CharField(max_length=300, verbose_name='Hash', null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de aprobación', null=True, blank=True)
    estado = models.ForeignKey(EstadoArchivo, on_delete=models.DO_NOTHING, verbose_name='Estado de Archivo', null=False,
                               blank=False)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario', null=False,
                                blank=False)

    def __str__(self):
        return self.documento.nombre

    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'Archivo':
        """
        Crea una instancia de Archivo con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el docuemento.
        :return: Instacia de Documento con la información especificada en el diccionario.
        """
        archivo = Archivo()
        archivo.documento_id = datos.get('documento_id', '')
        archivo.version = datos.get('version', '')
        archivo.notas = datos.get('notas', '')
        archivo.fecha_documento = datos.get('fecha_documento', '')
        archivo.archivo = datos.get('archivo', None)
        archivo.enlace = datos.get('enlace', '')
        archivo.hash = datos.get('hash', '')
        archivo.cadena_aprobacion_id = datos.get('cadena_aprobacion_id', '')
        archivo.estado_id = datos.get('estado_id', '')

        return archivo

    @property
    def nombre_documento(self):
        return '{0} {1}'.format(self.documento.codigo, self.documento.nombre) + \
               (' v{}'.format(self.version) if self.version != 0 else '')


class ResultadosAprobacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario', null=True,
                                blank=False)
    estado = models.ForeignKey(EstadoArchivo, on_delete=models.DO_NOTHING, verbose_name='Estado', null=False,
                               blank=False)
    comentario = models.CharField(max_length=255, verbose_name='Comentario', null=True, blank=False)
    fecha = models.DateTimeField(verbose_name='Fecha', null=False, blank=False)
    archivo = models.ForeignKey(Archivo, on_delete=models.DO_NOTHING, verbose_name='Archivo', null=False, blank=False)
    aprobacion_anterior = models.SmallIntegerField(verbose_name='Aprobación Anterior', null=True, blank=False)

    def __str__(self):
        return self.usuario.first_name

    class Meta:
        verbose_name = 'Resultado de Aprobación'
        verbose_name_plural = 'Resultados de Aprobaciones'


class GruposDocumentosProcesos(models.Model):
    grupo_documento = models.ForeignKey(GrupoDocumento, on_delete=models.DO_NOTHING, verbose_name='Grupo de Documento',
                                        null=True, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=False)

    def __str__(self):
        return 'Grupo Documento {0} - Proceso {1}'.format(self.grupo_documento, self.proceso)

    class Meta:
        verbose_name = 'Grupo de Documento Proceso'
        verbose_name_plural = 'Grupos de Documentos Procesos'



