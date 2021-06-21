from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

import GestionActividades
from Administracion.models import Proceso
from EVA.General import app_date_now
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from GestionActividades.Enumeraciones import EstadosActividades
from Proyectos.models import Contrato
from EVA import settings


class GrupoActividad(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=500, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False,)
    fecha_crea = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=False)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)
    grupo_actividad = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Grupo Actividad', null=True,
                                        blank=False)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Crea',
                                     null=False, blank=False, related_name='GrupoActividad_usuario_crea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Modifica',
                                         null=False, blank=False, related_name='GrupoActividad_usuario_Modifica')
    motivo = models.TextField(max_length=500, verbose_name='motivo', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Grupo Actividad'
        verbose_name_plural = 'Grupo Actividades'


class Actividad(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    codigo = models.CharField(max_length=50, verbose_name='Código', null=False, blank=False)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio', null=False, blank=False)
    fecha_fin = models.DateField(verbose_name='Fecha Fin', null=False, blank=False)
    fecha_crea = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Supervisor', null=False, blank=False,
                                   related_name='actividad_supervisor')
    descripcion = models.TextField(max_length=500, verbose_name='Descripción', null=False, blank=False)
    estado = models.SmallIntegerField(choices=EstadosActividades.choices,
                                      verbose_name='Estado', null=False, blank=False)
    porcentaje_avance = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),
                                                    MaxValueValidator(100)], verbose_name='Porcentaje Avance',
                                                    null=False, blank=False)
    grupo_actividad = models.ForeignKey(GrupoActividad, on_delete=models.DO_NOTHING, verbose_name='Grupo Actividad',
                                        blank=True, null=True)
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Crea',
                                     null=False, blank=False, related_name='Actividad_usuario_crea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuario Modifica',
                                         null=False, blank=False, related_name='Actividad_usuario_Modifica')
    calificacion = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),
                                               MaxValueValidator(10)], verbose_name='Calificación',
                                               null=False, blank=False)
    motivo = models.TextField(max_length=500, verbose_name='motivo', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'


class ResponsableActividad(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    responsable = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Responsable',
                                    blank=False, null=False)
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING,
                                  verbose_name='Actividad', blank=False, null=False)

    def __str__(self):
        return '{0}-{1}'.format(self.responsable, self.actividad)

    class Meta:
        unique_together = (('responsable', 'actividad'),)
        verbose_name = 'Responsable Actividad'
        verbose_name_plural = 'Responsables Actividades'
