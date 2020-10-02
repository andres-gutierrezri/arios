from django.db.models import QuerySet

from Administracion.models import Parametro
from Administracion.models.parametros import G_FINANCIERO, G_FINANCIERO_S_FLUJO_CAJA


class ParametrosFlujoCaja:

    CORTE_EJECUCION = 'CORTE_EJECUCION'
    CORTE_ALIMENTACION = 'CORTE_ALIMENTACION'

    def __init__(self):
        self.__corte_ejecucion:int = 10
        self.__corte_alimentacion:int = 10

    def get_corte_ejecucion(self) -> int:
        return self.__corte_ejecucion

    def set_corte_ejecucion(self, dia:int):
        self.__corte_ejecucion = dia

    def get_corte_alimentacion(self) -> int:
        return self.__corte_alimentacion

    def set_corte_alimentacion(self, dia:int):
        self.__corte_alimentacion = dia


class ParametrosFinancieros:

    @staticmethod
    def get_all() -> QuerySet:
        return Parametro.objects.filter(grupo=G_FINANCIERO, estado=True)

    @staticmethod
    def get_params_flujo_caja() -> ParametrosFlujoCaja:
        parametros_fc = ParametrosFlujoCaja()

        for parametro in ParametrosFinancieros.get_all().only('nombre', 'valor')\
                .filter(subgrupo=G_FINANCIERO_S_FLUJO_CAJA):
            try:
                if parametro.nombre == ParametrosFlujoCaja.CORTE_ALIMENTACION:
                    parametros_fc.set_corte_alimentacion(int(parametro.valor))
                elif parametro.nombre == ParametrosFlujoCaja.CORTE_EJECUCION:
                    parametros_fc.set_corte_alimentacion(int(parametro.valor))
            except ValueError:
                pass

        return parametros_fc






