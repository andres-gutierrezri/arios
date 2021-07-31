from django.db import models


class EstadosActividades(models.IntegerChoices):

    CREADA = 1, 'Creada'
    EN_PROCESO = 2, 'En Proceso'
    FINALIZADO = 3, 'Finalizado'
    CERRADA = 4, 'Cerrada'
    REABIERTA = 5, 'Reabierta'
    ANULADA = 6, 'Anulada'


class AsociadoGrupoActividades(models.IntegerChoices):

    CONTRATO = 1, 'Contrato'
    PROCESO = 2, 'Proceso'


class EstadosModificacionActividad(models.IntegerChoices):

    PENDIENTE = 1, 'Pendiente'
    APROBADA = 2, 'Aprobada'
    RECHAZADA = 3, 'Rechazada'


class TiposUsuariosActividad(models.IntegerChoices):

    NO_ASIGNADO = 1, 'No Asignado'
    SUPERVISOR = 2, 'Supervisor'
    RESPONSABLE = 3, 'Responsable'
