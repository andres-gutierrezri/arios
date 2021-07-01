# -*- coding: utf-8 -*-
import json

from django.forms import model_to_dict
from django.http import JsonResponse

from EVA.General.jsonencoders import AriosJSONEncoder


class ModelDjangoExtensiones:
    def __init__(self):
        pass

    def to_json(self, campos=None, excluir=None):
        """
            Retorna un string JSON del modelo.

            ``campos`` es una lista opcional con nombres de campos. Si es proporcionada,
            solo los campos nombrados serán incluidos en el string JSON, siempre y cuando
            pertenezcan al modelo.

            ``excluir`` es una lista opcional con nombres de campos. Si es proporcionada,
            los campos nombrados serán incluidos en el string JSON.
        """
        return json.dumps(model_to_dict(self, fields=campos, exclude=excluir), cls=AriosJSONEncoder)

    def to_dict(self, campos=None, excluir=None):
        """
            Retorna un diccionario de los campos del modelo.

            ``campos`` es una lista opcional con nombres de campos. Si es proporcionada,
            solo los campos nombrados serán incluidos en el diccionario, siempre y cuando
            pertenezcan al modelo.

            ``excluir`` es una lista opcional con nombres de campos. Si es proporcionada,
            los campos nombrados serán incluidos en el diccionario.
        """
        return model_to_dict(self, fields=campos, exclude=excluir)

    def comparar(self, otro, campos=None, excluir=None) -> bool:
        """
        Compara dos instancias de modelos para ver si tienen los mismos valores en sus campos.
        :param otro: La instancia con la que se quiere realizar la comparación.
        :param campos: Es una lista opcional con nombres de campos. Si es proporcionada,
            solo los campos nombrados serán incluidos en la comparación.
        :param excluir: Es una lista opcional con nombres de campos. Si es proporcionada,
            los campos nombrados serán excluidos de la comparación.
        :return: True si son iguales de lo contrario False.
        """
        if isinstance(otro, type(self)):
            return self.to_dict(campos, excluir) == otro.to_dict(campos, excluir)

        return False


class RespuestaJson:
    """
    Clase para generar respuestas estándar en JSON cuando se requiera.
    """
    def __init__(self, estado: str = 'OK', mensaje: str = '', datos=None):
        self.__estado: str = estado
        self.__mensaje: str = mensaje
        self.__datos = datos

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, value: str):
        self.__estado = value

    @property
    def mensaje(self):
        return self.__mensaje

    @mensaje.setter
    def mensaje(self, value: str):
        self.__mensaje = value

    @estado.setter
    def estado(self, value: str):
        self.__estado = value

    @property
    def datos(self):
        return self.__datos

    @datos.setter
    def datos(self, value: str):
        self.__mensaje = value

    def get_jsonresponse(self) -> JsonResponse:
        return JsonResponse({'estado': self.__estado, 'mensaje': self.__mensaje, 'datos': self.__datos})

    @staticmethod
    def exitosa(datos=None, mensaje: str = '') -> JsonResponse:
        """
        Genera una respuesta JSON estándar que indica que fue exitosa.
        :param datos: Datos a adjuntar a la respuesta, debe poderse convertir a JSON.
        :param mensaje: Mensaje de exitoso a enviar.
        :return: JsonResponse con el JSON estándar exitoso. {"estado": "OK", "mensaje": "", "datos": ""}.
        """
        return RespuestaJson(datos=datos, mensaje=mensaje).get_jsonresponse()

    @staticmethod
    def error(mensaje: str = '') -> JsonResponse:
        """
        Genera una respuesta JSON estándar que indica se presentó un error.
        :param mensaje: Descripción del error a enviar.
        :return: JsonResponse con el JSON estándar de error. exitoso {"estado": "error", "mensaje": "", "datos": null}.
        """
        return RespuestaJson(estado="error", mensaje=mensaje).get_jsonresponse()
