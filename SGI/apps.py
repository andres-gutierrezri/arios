from django.apps import AppConfig

from EVA.permisos import incluir_permisos_app


class SgiConfig(AppConfig):
    name = 'SGI'
    incluir_permisos_app('SGI.permisos')
