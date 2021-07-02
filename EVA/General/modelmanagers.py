import json

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, F

from EVA.General.jsonencoders import AriosJSONEncoder


class ManagerGeneral(models.Manager):
    """
    Clase de tipo models.Manager  que implementa algunas consultas que se pueden utilizar en varios modelos
    sobretodo aquellos que se va a utilizar en selectores.
    """
    def __init__(self, campo_texto: str = 'nombre'):
        super().__init__()
        self.campo_texto = campo_texto

    def get_xa_select(self) -> QuerySet:
        return self.get_x_estado(xa_select=True)

    def get_xa_select_x_empresa(self, id_empresa) -> QuerySet:
        return super().get_queryset().filter(empresa_id=id_empresa)\
            .values(campo_valor=F('id'), campo_texto=F(self.campo_texto)) \
            .order_by(self.campo_texto)

    def get_xa_select_activos(self) -> QuerySet:
        return self.get_x_estado(True, True)

    def get_xa_select_inactivos(self) -> QuerySet:
        return self.get_x_estado(False, True)

    def get_xa_select_activos_like_json(self) -> json:
        datos = []
        for dt in self.get_x_estado(True, True):
            datos.append({'campo_valor': dt['campo_valor'], 'campo_texto': dt['campo_texto']})
        return json.dumps(datos, cls=AriosJSONEncoder)

    def get_x_estado(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        filtro = {}

        if estado is not None and 'estado' in self.model._meta._forward_fields_map:
            filtro['estado'] = estado
        if xa_select:
            return super().get_queryset().filter(**filtro).values(campo_valor=F('id'), campo_texto=F(self.campo_texto))\
                .order_by(self.campo_texto)
        else:
            return super().get_queryset().filter(**filtro)


class ModeloBase(models.Model):

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='%(app_label)s_%(class)s_usuario_crea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica",
                                         null=True, blank=True,
                                         related_name='%(app_label)s_%(class)s_usuario_modifica')

    class Meta:
        abstract = True
