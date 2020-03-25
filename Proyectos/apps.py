from django.apps import AppConfig
from EVA.permisos import incluir_permisos_app


class ProyectosConfig(AppConfig):
    name = 'Proyectos'
    incluir_permisos_app('Proyectos.permisos')
