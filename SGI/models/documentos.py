from django.db import models
from EVA.General.conversiones import string_to_date
# Create your models here.
from Administracion.models import Empresa, Proceso


class GrupoDocumento(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.CharField(max_length=100, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Grupo de documento'
        verbose_name_plural = 'Grupos de documentos'


class CadenaAprobacionEncabezado(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cadena de aprobación'
        verbose_name_plural = 'Cadenas de aprobaciones'


class Documento(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    codigo = models.CharField(max_length=20, verbose_name='Código', null=False, blank=False)
    fecha = models.DateTimeField(verbose_name='Fecha', null=False, blank=False)
    version = models.DecimalField(verbose_name='Versión', max_digits=2, decimal_places=2, null=False, blank=False)
    cadena_aprobacion = models.ForeignKey(CadenaAprobacionEncabezado, on_delete=models.DO_NOTHING,
                                          verbose_name='Cadena de aprobación', null=True, blank=False)
    grupo_documento = models.ForeignKey(GrupoDocumento, on_delete=models.DO_NOTHING,
                                        verbose_name='Grupo de documento', null=True, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=False)

    def __str__(self):
        return self.nombre

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
        documento.fecha = string_to_date(datos.get('fecha', ''))
        documento.version = datos.get('version', '')
        documento.cadena_aprobacion_id = datos.get('cadena_aprobacion_id', '')
        documento.grupo_documento_id = datos.get('grupo_documento_id', '')
        documento.proceso_id = datos.get('proceso_id', '')

        return documento



