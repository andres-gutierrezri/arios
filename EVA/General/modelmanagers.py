from django.db import models
from django.db.models import QuerySet, F


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

    def get_xa_select_activos(self) -> QuerySet:
        return self.get_x_estado(True, True)

    def get_xa_select_inactivos(self) -> QuerySet:
        return self.get_x_estado(False, True)

    def get_x_estado(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        filtro = {}

        if estado is not None and 'estado' in self.model._meta._forward_fields_map:
            filtro['estado'] = estado
        if xa_select:
            return super().get_queryset().filter(**filtro).values(campo_valor=F('id'), campo_texto=F(self.campo_texto))\
                .order_by(self.campo_texto)
        else:
            return super().get_queryset().filter(**filtro)
