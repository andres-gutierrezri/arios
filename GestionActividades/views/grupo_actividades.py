import json
from datetime import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import lower
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Proceso, TipoContrato
from Administracion.utils import get_id_empresa_global
from EVA.General import app_datetime_now
from EVA.General.modeljson import RespuestaJson
from EVA.views.index import AbstractEvaLoggedView
from GestionActividades.Enumeraciones import PertenenciaGrupoActividades
from GestionActividades.models import GrupoActividad
from GestionActividades.models.models import Actividad, ResponsableActividad
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador
from TalentoHumano.models.colaboradores import ColaboradorProceso


class GruposActividadesIndexView(AbstractEvaLoggedView):
    def get(self, request):
        grupos_actividades = GrupoActividad.objects.get_xa_select_activos().values('id', 'nombre',
                                                                                   'contrato_id', 'proceso_id')
        actividades = Actividad.objects.values('id', 'grupo_actividad_id', 'estado')
        contratos = Contrato.objects.get_xa_select_activos()
        procesos = Proceso.objects.get_xa_select_activos()
        colaboradores = Colaborador.objects.get_xa_select_activos()
        responsables = User.objects.values('id', 'first_name', 'last_name')

        lista_procesos = Proceso.objects.get_xa_select_activos().values('id', 'nombre')
        lista_contratos = Contrato.objects.get_xa_select_activos().values('id', 'numero_contrato')

        datos_grupo = []
        indice = 0
        for grupo in grupos_actividades:
            conteo_actividades = 0
            actividades_pendientes = 0
            progreso = 0
            lista_actividades = []
            lista_users = []
            datos_grupo.append({'id_grupo': grupo['id'], 'nombre': '', 'actividades': conteo_actividades,
                                'actividades_pendientes': actividades_pendientes, 'progreso_porcentaje': progreso})
            for actividad in actividades:
                if grupo['id'] == actividad['grupo_actividad_id']:
                    lista_actividades.append(actividad['id'])
                    for lista in lista_actividades:
                        list_id_user = ResponsableActividad.objects.get_ids_responsables_list(lista)
                        for id_user in list_id_user:
                            if id_user not in lista_users:
                                lista_users.append(id_user)
                    conteo_actividades += 1
                    if actividad['estado'] != 4:
                        actividades_pendientes += 1
            for responsable in responsables:
                if responsable['id'] in lista_users:
                    datos_grupo[int(indice)]['nombre'] += (responsable['first_name'] + ' ' +
                                                           responsable['last_name'] + ', ')
            if conteo_actividades - actividades_pendientes != 0:
                progreso = int(((conteo_actividades - actividades_pendientes)/conteo_actividades)*100)

            datos_grupo[int(indice)]['actividades'] += conteo_actividades
            datos_grupo[int(indice)]['actividades_pendientes'] += actividades_pendientes
            datos_grupo[int(indice)]['progreso_porcentaje'] += progreso
            indice += 1

        return render(request, 'GestionActividades/GrupoActividades/index.html',
                      {'grupos_actividades': grupos_actividades,
                       'actividades': actividades,
                       'fecha': app_datetime_now(),
                       'contratos': contratos,
                       'colaboradores': colaboradores,
                       'lista_procesos': lista_procesos,
                       'lista_contratos': lista_contratos,
                       'datos_grupo': datos_grupo,
                       'procesos': procesos})


class GruposActividadesCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionActividades/GrupoActividades/_crear_editar_grupos_actividades_modal.html',
                      datos_xa_render(request))

    def post(self, request):
        grupo_actividad = GrupoActividad.from_dictionary(request.POST)
        grupo_actividad.usuario_crea = request.user
        grupo_actividad.usuario_modifica = request.user
        grupo_actividad.fecha_crea = app_datetime_now()

        if grupo_actividad.grupo_actividad_id == '':
            grupo_actividad.grupo_actividad_id = None
        if grupo_actividad.tipo_asociado == '1':
            grupo_actividad.proceso_id = None
        if grupo_actividad.tipo_asociado == '2':
            grupo_actividad.contrato_id = None

        if GrupoActividad.objects.filter(nombre__iexact=grupo_actividad.nombre,
                                         grupo_actividad_id__exact=grupo_actividad.grupo_actividad_id).exists():
            return RespuestaJson.error("Falló crear. Ya existe un grupo con el mismo nombre")

        else:
            grupo_actividad.save()

        return RespuestaJson.exitosa()


class GruposActividadesEditarView(AbstractEvaLoggedView):
    def get(self, request, id_grupo):
        grupo_actividad = GrupoActividad.objects.get(id=id_grupo)

        return render(request, 'GestionActividades/GrupoActividades/_crear_editar_grupos_actividades_modal.html',
                      datos_xa_render(request, grupo_actividad))

    def post(self, request, id_grupo):
        update_fields = ['fecha_modificacion', 'contrato_id', 'proceso_id', 'nombre', 'descripcion', 'fecha_crea',
                         'tipo_asociado', 'motivo', 'usuario_modifica', 'usuario_crea', 'grupo_actividad_id']

        grupo_actividad = GrupoActividad.from_dictionary(request.POST)
        grupo_actividad_db = GrupoActividad.objects.get(id=id_grupo)
        grupo_actividad.fecha_crea = grupo_actividad_db.fecha_crea
        grupo_actividad.fecha_modificacion = app_datetime_now()
        grupo_actividad.id = grupo_actividad_db.id
        grupo_actividad.usuario_modifica = request.user
        grupo_actividad.usuario_crea = grupo_actividad_db.usuario_crea

        if grupo_actividad.grupo_actividad_id == '':
            grupo_actividad.grupo_actividad_id = None
        if grupo_actividad.tipo_asociado == '1':
            grupo_actividad.proceso_id = None
        if grupo_actividad.tipo_asociado == '2':
            grupo_actividad.contrato_id = None

        try:
            grupo_actividad.full_clean(validate_unique=False)
        except ValidationError as errores:
            return RespuestaJson.error("Falló editar. Valide los datos ingresados al editar el grupo de actividades")

        if grupo_actividad_db.comparar(grupo_actividad, excluir=['fecha_modificacion', 'motivo']):
            return RespuestaJson.error("No se hicieron cambios en el grupo de actividades")

        else:
            grupo_actividad.save(update_fields=update_fields)

        return RespuestaJson.exitosa()


def datos_xa_render(request, grupo_actividad: GrupoActividad = None) -> dict:
    tipo_asociado = [{'campo_valor': 1, 'campo_texto': 'Contrato'},
                     {'campo_valor': 2, 'campo_texto': 'Proceso'}]

    grupos = GrupoActividad.objects.values('id', 'nombre')
    lista_grupos = []
    for grupo in grupos:
        lista_grupos.append({'campo_valor': grupo['id'], 'campo_texto': grupo['nombre']})

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

    opciones_contrato_proceso = [{'valor': 1, 'texto': 'Contrato'},
                                 {'valor': 2, 'texto': 'Proceso'}]

    datos = {'fecha': app_datetime_now(),
             'contratos': lista_contratos,
             'procesos': lista_procesos,
             'tipo_asociado': tipo_asociado,
             'grupos': lista_grupos,
             'opciones_contrato_proceso': opciones_contrato_proceso,
             'menu_actual': 'grupo-actividades'}

    if grupo_actividad:
        datos['grupo_actividad'] = grupo_actividad
        datos['editar'] = True

    return datos
