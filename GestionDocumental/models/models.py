from django.contrib.auth.models import User
from django.db import models

from EVA.General.modelmanagers import ManagerGeneral
from Proyectos.models import Contrato


class ConsecutivoDocumento(models.Model):
    objects = ManagerGeneral()
    consecutivo = models.CharField(max_length=50, verbose_name='Consecutivo', null=False, blank=False)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha', null=False, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)
    detalle = models.CharField(max_length=100, verbose_name='Detalle', null=False, blank=False)
    destinatario = models.CharField(max_length=100, verbose_name='Destinatario', null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null=False, blank=False)
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Consecutivo Documento'
        verbose_name_plural = 'Consecutivos Documentos'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ConsecutivoDocumento':
        """
        Crea una instancia de ConsecutivoDocumento con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Consecutivo de Documento.
        :return: Instacia de consecutivo de documento con la información especificada en el diccionario.
        """
        consecutivo = ConsecutivoDocumento()
        consecutivo.contrato_id = datos.get('contrato_id', None)
        consecutivo.detalle = datos.get('detalle', '')
        consecutivo.destinatario = datos.get('destinatario', '')

        return consecutivo
