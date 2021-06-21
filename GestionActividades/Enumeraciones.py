from django.db import models


class EstadosActividades(models.IntegerChoices):

    CREADA = 1, 'Creada'
    EN_PROCESO = 2, 'En Proceso'
    FINALIZADO = 3, 'Finalizado'
    CERRADA = 4, 'Cerrada'
    REABIERTA = 5, 'Reabierta'
