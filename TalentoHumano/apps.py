from django.apps import AppConfig
from EVA.permisos import incluir_permisos_app


class TalentohumanoConfig(AppConfig):
    name = 'TalentoHumano'
    incluir_permisos_app('TalentoHumano.permisos')
