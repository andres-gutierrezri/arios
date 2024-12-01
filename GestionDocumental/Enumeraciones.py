from django.db import models


class TiposActas(models.IntegerChoices):

    TODAS = 0, 'Todas'
    SUSPENSION = 1, 'Acta de suspensión'
    REINICIO = 2, 'Acta de reinicio'
    AMPLIACION = 3, 'Acta de ampliación de la suspensión'

    @classmethod
    def sigla(cls, tipo) -> str:
        """
        Determina la sigla según el tipo de acta.
        :param tipo: Tipo de acta para el que se quiere determinar la sigla.
        :return: String con la sigla, en caso de ser un tipo inválido retorna un string vacío.
        """
        if tipo == cls.SUSPENSION:
            return 'AS'
        elif tipo == cls.REINICIO:
            return 'AR'
        elif tipo == cls.AMPLIACION:
            return 'AAS'
        else:
            return ''
