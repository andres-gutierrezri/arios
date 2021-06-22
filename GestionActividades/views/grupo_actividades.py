import json
from datetime import datetime
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Proceso, TipoContrato
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from GestionActividades.Enumeraciones import PertenenciaGrupoActividades
from GestionActividades.models import GrupoActividad
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador
from TalentoHumano.models.colaboradores import ColaboradorProceso


class GruposActividadesIndexView(AbstractEvaLoggedView):
    def get(self, request):
        grupos_actividades = GrupoActividad.objects.get_xa_select_activos().values('id', 'nombre')
        contratos = Contrato.objects.get_xa_select_activos()
        procesos = Proceso.objects.get_xa_select_activos()
        colaboradores = Colaborador.objects.get_xa_select_activos()

        return render(request, 'GestionActividades/GrupoActividades/index.html',
                      {'grupos_actividades': grupos_actividades,
                       'contratos': contratos,
                       'colaboradores': colaboradores,
                       'procesos': procesos})


class GruposActividadesCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionActividades/GrupoActividades/modal_crear_editar_grupos_actividades.html',
                      datos_xa_render(request))


class GruposActividadesEditarView(AbstractEvaLoggedView):
    def get(self, request, id_grupo):
        grupo_actividad = GrupoActividad.objects.get(id=id_grupo)

        return render(request, 'GestionActividades/GrupoActividades/modal_crear_editar_grupos_actividades.html',
                      datos_xa_render(request, grupo_actividad))


def datos_xa_render(request, grupo_actividad: GrupoActividad = None) -> dict:
    tipo_pertenencia = [{'campo_valor': 1, 'campo_texto': 'Contrato'},
                        {'campo_valor': 2, 'campo_texto': 'Proceso'}]

    grupo_actividades = GrupoActividad.objects
    extra_tipos_pertenencia = []
    for tipo_grupo in grupo_actividades.all():
        extra_tipos_pertenencia.append({'id': tipo_grupo.id, 'tipo_pertenencia': tipo_grupo.tipo_pertenencia})

    print(extra_tipos_pertenencia)
    contratos = Contrato.objects \
        .filter(empresa_id=get_id_empresa_global(request)) \
        .values('id', 'numero_contrato', 'cliente__nombre')

    lista_contratos = []
    for contrato in contratos:
        lista_contratos.append({'campo_valor': contrato['id'], 'campo_texto': '{0} - {1}'
                               .format(contrato['numero_contrato'], contrato['cliente__nombre'])})

    procesos = Proceso.objects \
        .filter(empresa_id=get_id_empresa_global(request)) \
        .values('id', 'nombre')

    lista_procesos = []
    for proceso in procesos:
        lista_procesos.append({'campo_valor': proceso['id'], 'campo_texto': proceso['nombre']})

    datos = {
        'contratos': lista_contratos,
        'procesos': lista_procesos,
        'lista_procesos': lista_procesos,
        'tipo_pertenencia': tipo_pertenencia,
        'extra_tipos_pertenencia': json.dumps(extra_tipos_pertenencia),
        'grupo_actividades': grupo_actividades,
        'menu_actual': 'grupo-actividades'}

    if grupo_actividad:
        datos['grupo_actividad'] = grupo_actividad
        datos['editar'] = True

    return datos
