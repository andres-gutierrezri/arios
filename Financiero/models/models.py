from django.db import models

from EVA.General.modelmanagers import ManagerGeneral


class EntidadBancaria(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)
    codigo_banco = models.CharField(verbose_name='Código del Banco', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Entidad Bancaria'
        verbose_name_plural = 'Entidades Bancarias'


class ActividadEconomica(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)
    codigo_ciiu = models.CharField(verbose_name='Codigo CIIU', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Actividad Económica'
        verbose_name_plural = 'Actividades Económicas'


class TipoPersona(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Persona'
        verbose_name_plural = 'Tipos de Personas'


class TipoContribuyente(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Contribuyente'
        verbose_name_plural = 'Tipos de Contribuyentes'


class Regimen(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(verbose_name='Nombre', max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Régimen'
        verbose_name_plural = 'Regímenes'
