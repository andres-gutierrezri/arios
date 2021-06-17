from django.db import models


class Estado(models.IntegerChoices):

    EN_PROCESO = 1, 'En Proceso'
    FINALIZADO = 2, 'Finalizado'
    CERRADA = 3, 'Cerrada'
    REABIERTA = 4, 'Reabierta'
