from django.apps import AppConfig
from EVA.permisos import incluir_permisos_app


class FinancieroConfig(AppConfig):
    name = 'Financiero'
    incluir_permisos_app('Financiero.permisos')