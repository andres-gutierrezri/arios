from django.db import models


class TipoCuentaBancaria(models.IntegerChoices):
    CORRIENTE = 1, 'Cuenta Corriente'
    AHORROS = 2, 'Cuenta de Ahorros'
    BANCARIA = 3, 'Bancaria'
