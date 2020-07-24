from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models

from EVA.General.modeljson import ModelDjangoExtensiones


class PermisosFuncionalidad(models.Model, ModelDjangoExtensiones):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.CharField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, verbose_name='Content Type',
                                     null=True, blank=True)
    grupo = models.ForeignKey(Group, on_delete=models.DO_NOTHING, verbose_name='Grupo', null=True, blank=True)
    solo_admin = models.BooleanField(verbose_name='Solo Administrador', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Permisos de Funcionalidad'
        verbose_name_plural = 'Permisos de Funcionalidades'
