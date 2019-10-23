# -*- coding: utf-8 -*-
import json

from django.forms import model_to_dict

from EVA.General.jsonencoders import AriosJSONEncoder


class ModelDjangoJSON:
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
