from importlib import import_module
from typing import List


class Permiso:
    def __init__(self, nombre_url: str, permisos: []):
        self.nombre_url: str = nombre_url
        self.permisos: List = permisos


permisos_eva = {}


def incluir_permisos_app(modulo: str):
    app_name = None
    modulo_permisos = import_module('SGI.permisos')
    permisos = getattr(modulo_permisos, 'permisos', modulo_permisos)
    app_name = getattr(modulo_permisos, 'app_name', app_name)
    permisos_eva[app_name] = permisos


def get_permisos_eva():
    return permisos_eva



