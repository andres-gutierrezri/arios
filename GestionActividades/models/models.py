from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import QuerySet

import GestionActividades
from Administracion.models import Proceso
from EVA.General import app_date_now
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral
from GestionActividades.Enumeraciones import EstadosActividades, AsociadoGrupoActividades, \
    EstadosModificacionActividad
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
    tipo_asociado = models.SmallIntegerField(choices=AsociadoGrupoActividades.choices,
                                             verbose_name='Asociado', null=False, blank=False)
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
        grupo_actividad.grupo_actividad_id = datos.get('grupo_asociado', None)
        grupo_actividad.descripcion = datos.get('descripcion', '')
        grupo_actividad.tipo_asociado = datos.get('tipo_asociado', '')
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
    tiempo_estimado = models.DecimalField(max_digits=7, decimal_places=2, default=0,
                                          verbose_name='Tiempo Estimado', null=False, blank=False)
    horas_invertidas = models.DecimalField(max_digits=7, decimal_places=2, default=0,
                                           verbose_name='Horas Invertidas', null=False, blank=False)
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
        actividad.grupo_actividad_id = datos.get('grupo_asociado', None)
        actividad.descripcion = datos.get('descripcion', '')
        actividad.tiempo_estimado = datos.get('tiempo_estimado', '')
        actividad.motivo = datos.get('motivo', '')
        actividad.estado = datos.get('estado', 1)
        actividad.codigo = datos.get('codigo', 1)
        actividad.calificacion = datos.get('calificacion', 0)
        actividad.porcentaje_avance = datos.get('porcentaje', 0)
        actividad.soporte_requerido = datos.get('soporte_requerido', False)

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
        return 'Responsable: {0} - Actividad: {1}'.format(self.responsable, self.actividad)

    class Meta:
        unique_together = (('responsable', 'actividad'),)


def custom_upload_to(instance, filename):
    return '{2}/GestiónActividades/Actividades/Soportes/{0} {1}' \
     .format(instance.actividad.codigo, filename, settings.EVA_PRIVATE_MEDIA)


class SoporteActividad(models.Model):
    objects = ManagerGeneral()
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING, verbose_name='Actividad', blank=False,
                                  null=False)
    archivo = models.FileField(upload_to=custom_upload_to, blank=False, max_length=250)
    descripcion = models.TextField(max_length=500, verbose_name='Descripción', null=False, blank=False)
    fecha_fin = models.DateField(verbose_name='Fecha Fin', null=False, blank=False)
    motivo = models.TextField(max_length=500, verbose_name='motivo', null=False, blank=False)

    def __str__(self):
        return self.actividad.nombre

    class Meta:
        verbose_name = 'Soporte'
        verbose_name_plural = 'Soportes'

    @staticmethod
    def from_dictionary(datos: dict) -> 'SoporteActividad':
        """
        Crea una instancia de los Soportes con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para cargar los Soportes.
        :return: Instacia de los Soportes con la información especificada en el diccionario.
        """

        soporte = SoporteActividad()
        soporte.descripcion = datos.get('descripcion', '')
        soporte.fecha_fin = datos.get('fecha_final', '')
        soporte.motivo = datos.get('motivo', '')

        return soporte


class AvanceActividad(models.Model):
    objects = ManagerGeneral()
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING, verbose_name='Actividad', blank=False,
                                  null=False)
    descripcion = models.TextField(max_length=500, verbose_name='Descripción', null=False, blank=False)
    fecha_avance = models.DateField(verbose_name='Fecha Avance', null=False, blank=False)
    horas_empleadas = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Horas Empleadas',
                                          null=False, blank=False)
    porcentaje_avance = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),
                                                                           MaxValueValidator(100)],
                                                    verbose_name='Porcentaje Avance',
                                                    null=False, blank=False)
    responsable = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Responsable',
                                    blank=False, null=False)

    def __str__(self):
        return self.actividad.nombre

    class Meta:
        verbose_name = 'Avance'
        verbose_name_plural = 'Avances'

    @staticmethod
    def from_dictionary(datos: dict) -> 'AvanceActividad':
        """
        Crea una instancia de los Avances de una actividad con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para almacenar los avances de una actividad.
        :return: Instacia de los avances de una actividad con la información especificada en el diccionario.
        """

        avance_actividad = AvanceActividad()
        avance_actividad.descripcion = datos.get('descripcion', '')
        avance_actividad.fecha_avance = datos.get('fecha_avance', '')
        avance_actividad.horas_empleadas = datos.get('horas', '')
        avance_actividad.porcentaje_avance = datos.get('porcentaje', '')

        return avance_actividad


class ModificacionActividad(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING, verbose_name='Actividad', blank=False,
                                  null=False)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Supervisor', null=False, blank=False,
                                   related_name='modificación_actividad_supervisor')
    descripcion = models.TextField(max_length=500, verbose_name='Descripción', null=False, blank=False)
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio', null=False, blank=False)
    fecha_fin = models.DateField(verbose_name='Fecha Fin', null=False, blank=False)
    estado = models.SmallIntegerField(default=1, choices=EstadosModificacionActividad.choices,
                                      verbose_name='Estado', null=False, blank=False)
    grupo_actividad = models.ForeignKey(GrupoActividad, on_delete=models.DO_NOTHING, verbose_name='Grupo Actividad',
                                        blank=True, null=True)
    tiempo_estimado = models.DecimalField(max_digits=7, decimal_places=2, default=0,
                                          verbose_name='Tiempo Estimado', null=False, blank=False)
    motivo = models.TextField(max_length=500, verbose_name='motivo', null=False, blank=False)
    soporte_requerido = models.BooleanField(verbose_name='Soporte Requerido', blank=False, null=False, default=False)
    comentario_supervisor = models.TextField(max_length=500, verbose_name='comentario', null=False, blank=False)
    fecha_solicitud = models.DateTimeField(auto_now=True, verbose_name='Fecha de Solicitud', null=False,
                                           blank=False)
    fecha_respuesta_solicitud = models.DateTimeField(verbose_name='Fecha Respuesta de Solicitud', null=False,
                                                     blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Modificacion Actividad'
        verbose_name_plural = 'Modificaciones Actividad'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ModificacionActividad':
        """
        Crea una instancia de Actividad con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear Actividades.
        :return: Instacia de actividades con la información especificada en el diccionario.
        """
        modificacion_actividad = ModificacionActividad()
        modificacion_actividad.nombre = datos.get('_nombre', None)
        modificacion_actividad.supervisor_id = datos.get('_supervisor_id', None)
        modificacion_actividad.fecha_inicio = datos.get('_fecha_inicio', '')
        modificacion_actividad.fecha_fin = datos.get('_fecha_final', '')
        modificacion_actividad.grupo_actividad_id = datos.get('_grupo_asociado', None)
        modificacion_actividad.descripcion = datos.get('_descripcion', '')
        modificacion_actividad.tiempo_estimado = datos.get('_tiempo_estimado', '')
        modificacion_actividad.motivo = datos.get('_motivo', '')
        modificacion_actividad.estado = datos.get('estado', 1)
        modificacion_actividad.soporte_requerido = datos.get('_soporte_requerido', False)
        modificacion_actividad.comentario_supervisor = datos.get('comentario_supervisor', '')

        return modificacion_actividad


class ResponsableActividadModificacion(models.Model):
    responsable = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Responsable',
                                    blank=False, null=False)
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING,
                                  verbose_name='Actividad', blank=False, null=False)

    def __str__(self):
        return 'Responsable: {0} - Actividad: {1}'.format(self.responsable, self.actividad)

    class Meta:
        unique_together = (('responsable', 'actividad'),)
