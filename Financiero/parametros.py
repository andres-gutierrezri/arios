from django.db.models import QuerySet

from Administracion.models import Parametro
from Administracion.models.parametros import G_FINANCIERO, G_FINANCIERO_S_FLUJO_CAJA, G_FINANCIERO_S_FACELEC


class ParametrosFlujoCaja:

    CORTE_EJECUCION = 'CORTE_EJECUCION'
    CORTE_ALIMENTACION = 'CORTE_ALIMENTACION'

    def __init__(self):
        self.__corte_ejecucion: int = 10
        self.__corte_alimentacion: int = 10

    def get_corte_ejecucion(self) -> int:
        return self.__corte_ejecucion

    def set_corte_ejecucion(self, dia: int):
        self.__corte_ejecucion = dia

    def get_corte_alimentacion(self) -> int:
        return self.__corte_alimentacion

    def set_corte_alimentacion(self, dia: int):
        self.__corte_alimentacion = dia


class ParametrosFacelec:

    CORREO = 'CORREO'
    SOFTWARE_ID = 'SOFTWARE_ID'
    SOFTWARE_PIN = 'SOFTWARE_PIN'
    TEST_SET_ID = 'TEST_SET_ID'
    AMBIENTE = 'AMBIENTE'
    EN_HABILITACION = 'EN_HABILITACION'
    USUARIO_CERTIFICADO = 'USUARIO_CERTIFICADO'
    CLAVE_CERTIFICADO = 'CLAVE_CERTIFICADO'
    CORREO_COPIA = 'CORREO_COPIA'

    def __init__(self):
        self.__correo: str = ''
        self.__software_id: str = ''
        self.__software_pin: str = ''
        self.__test_set_id: str = ''
        self.__ambiente: str = '2'
        self.__en_habilitacion: bool = False
        self.__usuario_certificado: str = ''
        self.__clave_certificado: str = ''
        self.__correo_copia: str = ''

    def get_correo(self) -> str:
        return self.__correo

    def set_correo(self, correo: str):
        self.__correo = correo

    def get_software_id(self) -> str:
        return self.__software_id

    def set_software_id(self, software_id: str):
        self.__software_id = software_id

    def get_software_pin(self) -> str:
        return self.__software_pin

    def set_software_pin(self, software_pin: str):
        self.__software_pin = software_pin

    def get_test_set_id(self) -> str:
        return self.__test_set_id

    def set_test_set_id(self, test_set_id: str):
        self.__test_set_id = test_set_id

    def get_ambiente(self) -> str:
        return self.__ambiente

    def set_ambiente(self, ambiente: str):
        self.__ambiente = ambiente

    def get_en_habilitacion(self) -> bool:
        return self.__en_habilitacion

    def set_en_habilitacion(self, en_habilitacion: bool):
        self.__en_habilitacion = en_habilitacion

    def get_usuario_certificado(self) -> str:
        return self.__usuario_certificado

    def set_usuario_certificado(self, usuario_certificado: str):
        self.__usuario_certificado = usuario_certificado

    def get_clave_certificado(self) -> str:
        return self.__usuario_certificado

    def set_clave_certificado(self, clave_certificado: str):
        self.__usuario_certificado = clave_certificado

    def get_correo_copia(self) -> str:
        return self.__correo

    def set_correo_copia(self, correo_copia: str):
        self.__correo = correo_copia


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

    @staticmethod
    def get_params_facelec(empresa_id: int) -> ParametrosFacelec:
        parametros = ParametrosFacelec()

        for parametro in ParametrosFinancieros.get_all().only('nombre', 'valor')\
                .filter(subgrupo=G_FINANCIERO_S_FACELEC, empresa_id=empresa_id):
            try:
                if parametro.nombre == ParametrosFacelec.CORREO:
                    parametros.set_correo(parametro.valor)
                elif parametro.nombre == ParametrosFacelec.SOFTWARE_ID:
                    parametros.set_software_id(parametro.valor)
                elif parametro.nombre == ParametrosFacelec.SOFTWARE_PIN:
                    parametros.set_software_pin(parametro.valor)
                elif parametro.nombre == ParametrosFacelec.TEST_SET_ID:
                    parametros.set_test_set_id(parametro.valor)
                elif parametro.nombre == ParametrosFacelec.AMBIENTE:
                    parametros.set_ambiente(parametro.valor)
                elif parametro.nombre == ParametrosFacelec.EN_HABILITACION:
                    parametros.set_en_habilitacion(parametro.valor.lower() == 'true')
                elif parametro.nombre == ParametrosFacelec.USUARIO_CERTIFICADO:
                    parametros.set_usuario_certificado(parametro.valor)
                elif parametro.nombre == ParametrosFacelec.CLAVE_CERTIFICADO:
                    parametros.set_clave_certificado(parametro.valor)
                elif parametro.nombre == ParametrosFacelec.CORREO_COPIA:
                    parametros.set_correo_copia(parametro.valor)

            except ValueError:

                pass
        return parametros






