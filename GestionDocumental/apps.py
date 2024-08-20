from django.apps import AppConfig
from EVA.permisos import incluir_permisos_app


class GestiondocumentalConfig(AppConfig):
    name = 'GestionDocumental'
    incluir_permisos_app('GestionDocumental.permisos')
