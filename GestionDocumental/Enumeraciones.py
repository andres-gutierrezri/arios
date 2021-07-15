from django.db import models


class TiposActas(models.IntegerChoices):

    SUSPENSION = 0, 'Acta de suspensión'
    REINICIO = 1, 'Acta de reinicio'
    AMPLIACION = 2, 'Acta de ampliación de la suspensión'
