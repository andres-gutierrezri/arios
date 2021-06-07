from django.db import models


class MedioSoporte(models.IntegerChoices):

    DIGITAL = 1, 'Digital'
    IMPRESO = 2, 'Impreso'
    DIGITAL_IMPRESO = 3, 'Digital e impreso'


class TiempoConservacion(models.IntegerChoices):

    TIEMPO_5_A = 5, '5 Años'
    TIEMPO_20_A = 20, '20 Años'
