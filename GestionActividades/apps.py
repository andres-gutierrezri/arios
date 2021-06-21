from django.apps import AppConfig
from EVA.permisos import incluir_permisos_app


class GestionactividadesConfig(AppConfig):
    name = 'GestionActividades'
    incluir_permisos_app('GestionActividades.permisos')
