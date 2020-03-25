from django.apps import AppConfig
from EVA.permisos import incluir_permisos_app


class AdministracionConfig(AppConfig):
    name = 'Administracion'
    incluir_permisos_app('Administracion.permisos')
