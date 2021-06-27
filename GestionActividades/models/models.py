from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import QuerySet

import GestionActividades
from Administracion.models import Proceso
from EVA.General import app_date_now
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from GestionActividades.Enumeraciones import EstadosActividades, PertenenciaGrupoActividades
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
    tipo_pertenencia = models.SmallIntegerField(choices=PertenenciaGrupoActividades.choices,
                                                verbose_name='Pertenencia', null=False, blank=False)
    proceso = models.ForeignKey(Proceso, on_delete=models.DO_NOTHING, verbose_name='Proceso', null=True, blank=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name='Contrato', null=True, blank=True)
    grupo_actividad = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Grupo Actividad', null=True,
                                        blank=True)
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

    @staticmethod
    def from_dictionary(datos: dict) -> 'GrupoActividad':
        """
        Crea una instancia de GrupoActividad con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear el Grupo de Actividades.
        :return: Instacia de Grupo de actividades con la información especificada en el diccionario.
        """
        grupo_actividad = GrupoActividad()
        grupo_actividad.nombre = datos.get('nombre', None)
        grupo_actividad.contrato_id = datos.get('contrato_id', None)
        grupo_actividad.proceso_id = datos.get('proceso_id', None)
        grupo_actividad.grupo_actividad_id = datos.get('grupo_pertenece', None)
        grupo_actividad.descripcion = datos.get('descripcion', '')
        grupo_actividad.tipo_pertenencia = datos.get('tipo_pertenencia', '')
        grupo_actividad.motivo = datos.get('motivo', '')
        grupo_actividad.estado = True

        return grupo_actividad


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
    estado = models.SmallIntegerField(default=1, choices=EstadosActividades.choices,
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
    soporte_requerido = models.BooleanField(verbose_name='Soporte Requerido', blank=False, null=False, default=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    @staticmethod
    def from_dictionary(datos: dict) -> 'Actividad':
        """
        Crea una instancia de Actividad con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear Actividades.
        :return: Instacia de actividades con la información especificada en el diccionario.
        """
        actividad = Actividad()
        actividad.nombre = datos.get('nombre', None)
        actividad.supervisor_id = datos.get('supervisor_id', None)
        actividad.fecha_inicio = datos.get('fecha_inicio', '')
        actividad.fecha_fin = datos.get('fecha_final', '')
        actividad.grupo_actividad_id = datos.get('grupo_pertenece', None)
        actividad.descripcion = datos.get('descripcion', '')
        actividad.motivo = datos.get('motivo', '')
        actividad.estado = datos.get('estado', 1)
        actividad.codigo = datos.get('codigo', '100200')


        return actividad


class ResponsableActividadManger(models.Manager):
    def get_ids_responsables(self, actividad_id: int = None, actividad: Actividad = None) -> QuerySet:
        if actividad:
            actividad_id = actividad.id

        filtro = {}
        if actividad_id:
            filtro['actividad_id'] = actividad_id

        return super().get_queryset().filter(**filtro).values_list('responsable_id', flat=True)

    def get_ids_responsables_list(self, actividad_id: int = None,  actividad: Actividad = None) -> list:
        return list(self.get_ids_responsables(actividad_id, actividad))


class ResponsableActividad(models.Model):
    objects = ResponsableActividadManger()
    responsable = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Responsable',
                                    blank=False, null=False)
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING,
                                  verbose_name='Actividad', blank=False, null=False)

    def __str__(self):
        return str.format(self.responsable, self.actividad)

    class Meta:
        unique_together = (('responsable', 'actividad'),)




