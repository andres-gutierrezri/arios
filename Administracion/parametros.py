from django.db.models import QuerySet

from Administracion.models import Parametro
from Administracion.models.parametros import G_ADMINISTRACION, G_ADMINISTRACION_S_SALA_JUNTAS


class ParametrosSalaJuntas:

    HOLGURA = 'HOLGURA'

    def __init__(self):
        self.__holgura: int = 15

    def get_holgura(self) -> int:
        return self.__holgura

    def set_holgura(self, holgura: int):
        self.__holgura = holgura


class ParametrosAdministracion:

    @staticmethod
    def get_all() -> QuerySet:
        return Parametro.objects.filter(grupo=G_ADMINISTRACION, estado=True)

    @staticmethod
    def get_params_sala_juntas() -> ParametrosSalaJuntas:
        parametros_sj = ParametrosSalaJuntas()

        for parametro in ParametrosAdministracion.get_all().only('nombre', 'valor') \
                .filter(subgrupo=G_ADMINISTRACION_S_SALA_JUNTAS):
            try:
                if parametro.nombre == ParametrosSalaJuntas.HOLGURA:
                    parametros_sj.set_holgura(int(parametro.valor))
            except ValueError:
                pass

        return parametros_sj
