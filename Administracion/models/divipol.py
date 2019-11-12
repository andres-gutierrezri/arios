from django.db import models
from EVA.General.modeljson import ModelDjangoExtensiones

# Create your models here.
from EVA.General.modelmanagers import ManagerGeneral


class BaseDivipol(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()

    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    codigo_letras = models.TextField(max_length=4, verbose_name='Código', null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        abstract = True


class Pais(BaseDivipol):
    pass

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'


class Departamento(BaseDivipol):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, verbose_name='País', null=True, blank=False)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'


class Municipio(BaseDivipol):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, verbose_name='Departamento', null=True
                                     , blank=False)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'


class CentroPoblado(BaseDivipol):
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, verbose_name='Municipio', null=True, blank=False)

    class Meta:
        verbose_name = 'Centro Poblado'
        verbose_name_plural = 'Centros Poblados'
