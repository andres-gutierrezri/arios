from django.db import models
from django.db.models import F

from Administracion.models import Empresa


class TipoDocumento (models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.CharField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'

    # Tipos Fijos
    FACTURA = 1


class ConsecutivoDocumento (models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=False, blank=False)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.DO_NOTHING, verbose_name='Tipo de Documento',
                                       null=False, blank=False)
    consecutivo = models.PositiveIntegerField(verbose_name='Consecutivo', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return '{0}-{1}'.format(self.tipo_documento.nombre, self.consecutivo)

    class Meta:
        verbose_name = 'Consecutivo Documento'
        verbose_name_plural = 'Consecutivos Documento'
        unique_together = ('empresa', 'tipo_documento')

    @staticmethod
    def get_consecutivo_documento(tipo_documento_id, empresa_id):

        consecutivo = ConsecutivoDocumento.objects.filter(tipo_documento_id=tipo_documento_id, empresa_id=empresa_id).first()
        if consecutivo:
            consecutivo.consecutivo = F('consecutivo') + 1
            consecutivo.save(update_fields=['consecutivo'])
            consecutivo.refresh_from_db(fields=['consecutivo'])
        else:
            consecutivo = ConsecutivoDocumento(tipo_documento_id=tipo_documento_id, empresa_id=empresa_id, estado=True)
            consecutivo.consecutivo = 1
            consecutivo.save()

        return consecutivo.consecutivo