import json
import os
from _decimal import Decimal
from datetime import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import lower
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Proceso, TipoContrato
from Administracion.utils import get_id_empresa_global
from EVA.General import app_datetime_now, app_date_now
from EVA.General.modeljson import RespuestaJson
from EVA.views.index import AbstractEvaLoggedView
from GestionActividades.Enumeraciones import PertenenciaGrupoActividades, EstadosActividades
from GestionActividades.models.models import Actividad, GrupoActividad, ResponsableActividad, Soporte
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador
from TalentoHumano.models.colaboradores import ColaboradorProceso


class ActividadesIndexView(AbstractEvaLoggedView):
    def get(self, request, id=None):
        actividades = Actividad.objects.values('id', 'estado', 'fecha_inicio')

        for actividad in actividades:
            if actividad['fecha_inicio'] <= app_date_now() and actividad['estado'] == EstadosActividades.CREADA:
                actividad_db = Actividad.objects.get(id=actividad['id'])
                actividad_db.estado = EstadosActividades.EN_PROCESO
                actividad_db.save()

        responsable_actividad = ResponsableActividad.objects.values('responsable_id', 'actividad_id')
        colaboradores = User.objects.values('id', 'first_name', 'last_name')
        grupos = GrupoActividad.objects.values('id', 'nombre', 'grupo_actividad_id')
        search = request.GET.get('search', '')

        if search:
            grupos = grupos.filter(Q(nombre__icontains=search))

        if id:
            grupos = grupos.filter(Q(id=id) | Q(nombre__iexact='Generales') | Q(grupo_actividad_id=id))

        archivos_soporte = Soporte.objects.values('id', 'archivo', 'actividad_id')

        actividades = Actividad.objects.values('id', 'nombre', 'grupo_actividad_id', 'descripcion',
                                               'estado', 'porcentaje_avance', 'soporte_requerido', 'fecha_inicio')

        return render(request, 'GestionActividades/Actividades/index.html',
                      {'actividades': actividades,
                       'grupos': grupos,
                       'responsable_actividad': responsable_actividad,
                       'colaboradores': colaboradores,
                       'buscar': search,
                       'archivos_soporte': archivos_soporte,
                       'EstadosActividades': EstadosActividades,
                       'fecha': app_datetime_now()})


class ActividadesCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionActividades/Actividades/modal_crear_editar_actividades.html',
                      datos_xa_render(request))

    def post(self, request):
        grupo_actividad = GrupoActividad.from_dictionary(request.POST)
        actividad = Actividad.from_dictionary(request.POST)
        actividad.usuario_crea = request.user
        actividad.usuario_modifica = request.user
        actividad.fecha_crea = app_datetime_now()
        responsables = request.POST.getlist('responsables_id[]', None)

        if actividad.grupo_actividad_id == '':
            if GrupoActividad.objects.filter(nombre__iexact='generales').exists():
                grupo_generales = list(GrupoActividad.objects.values('id').filter(nombre__iexact='generales'))
                actividad.grupo_actividad_id = grupo_generales[0].get('id')
            else:
                return RespuestaJson.error("Falló crear. El grupo Generales no existe")

        if Actividad.objects.filter(nombre__iexact=actividad.nombre,
                                    grupo_actividad_id__exact=actividad.grupo_actividad_id).exists():
            return RespuestaJson.error("Falló crear. Ya existe una actividad con el mismo nombre dentro del grupo")

        elif GrupoActividad.objects.filter(nombre__iexact=actividad.nombre).exists():
            return RespuestaJson.error("Falló crear. No puede colocar el mismo nombre del grupo "
                                       "que va a contener la actividad")

        else:
            actividad.save()
            for responsable in responsables:
                ResponsableActividad.objects.create(responsable_id=responsable, actividad=actividad)

        return RespuestaJson.exitosa()


class ActividadesEditarView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        return render(request, 'GestionActividades/Actividades/modal_crear_editar_actividades.html',
                      datos_xa_render(request, actividad))

    def post(self, request, id_actividad):
        update_fields = ['fecha_modificacion', 'supervisor_id', 'fecha_inicio', 'fecha_fin', 'nombre', 'descripcion',
                         'fecha_crea', 'motivo', 'usuario_modifica', 'usuario_crea',
                         'grupo_actividad_id', 'estado', 'soporte_requerido']
        grupo_actividad = GrupoActividad.from_dictionary(request.POST)
        actividad = Actividad.from_dictionary(request.POST)
        actividad_db = Actividad.objects.get(id=id_actividad)
        actividad.fecha_crea = actividad_db.fecha_crea
        actividad.fecha_modificacion = app_datetime_now()
        actividad.id = actividad_db.id
        actividad.usuario_modifica = request.user
        actividad.usuario_crea = actividad_db.usuario_crea
        responsables = request.POST.getlist('responsables_id[]', None)
        actividad.soporte_requerido = request.POST.get('soporte_requerido', 'False') == 'True'

        if actividad.grupo_actividad_id == '':
            if GrupoActividad.objects.filter(nombre__iexact='generales').exists():
                grupo_generales = list(GrupoActividad.objects.values('id').filter(nombre__iexact='generales'))
                actividad.grupo_actividad_id = grupo_generales[0].get('id')
            else:
                return RespuestaJson.error("Falló crear. El grupo Generales no existe")

        responsables_actividad_db = ResponsableActividad.objects.filter(actividad_id=id_actividad)
        cantidad_responsables = responsables_actividad_db.count()
        conteo_responsables = 0
        if cantidad_responsables == len(responsables):
            for clb in responsables_actividad_db:
                for ctr in responsables:
                    if clb.responsable.id == int(ctr):
                        conteo_responsables += 1
        else:
            conteo_responsables = len(responsables)

        try:
            actividad.full_clean(validate_unique=False)
        except ValidationError as errores:
            return RespuestaJson.error("Falló editar. Valide los datos ingresados al editar la actividad")

        if GrupoActividad.objects.filter(nombre__iexact=actividad.nombre).exists():
            return RespuestaJson.error("Falló editar. No puede colocar el mismo nombre del grupo "
                                       "que va a contener la actividad")

        if actividad_db.comparar(actividad, excluir=['fecha_modificacion', 'motivo', 'calificacion', 'codigo',
                                                     'porcentaje_avance']) \
                and conteo_responsables == cantidad_responsables:
            return RespuestaJson.error("No se hicieron cambios en la actividad")

        else:
            actividad.save(update_fields=update_fields)
            ResponsableActividad.objects.filter(actividad_id=id_actividad).delete()
            for responsable in responsables:
                ResponsableActividad.objects.create(responsable_id=responsable, actividad_id=id_actividad)

        return RespuestaJson.exitosa()


class CargarSoporteView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)

        if actividad.estado == EstadosActividades.FINALIZADO:
            opciones_estado = [{'valor': 3, 'texto': 'Finalizada'}]
        else:
            opciones_estado = [{'valor': 2, 'texto': 'En proceso'},
                               {'valor': 3, 'texto': 'Finalizada'}]
        return render(request, 'GestionActividades/Actividades/modal_cargar_editar_soportes.html',
                      {'fecha': app_datetime_now(),
                       'actividad': actividad,
                       'opciones_estado': opciones_estado})

    def post(self, request, id_actividad):
        soporte = Soporte.from_dictionary(request.POST)


        update_fields = ['estado']
        actividad_db = Actividad.objects.get(id=id_actividad)
        actividad_db.estado = EstadosActividades.FINALIZADO
        actividad_db.save(update_fields=update_fields)
        # print(request)

        # soporte = Soporte.from_dictionary(request.POST)
        # soporte.save()

        return RespuestaJson.exitosa()


class CargarArchivoSoporteView(AbstractEvaLoggedView):
    def post(self, request, id_actividad):
        archivos = request.FILES.getlist('file')
        print(archivos)

        return RespuestaJson.exitosa()


class VerSoporteView(AbstractEvaLoggedView):
    def get(self, request, id_soporte, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        if Soporte.objects.filter(id=id_soporte).exists():
            soporte = Soporte.objects.get(id=id_soporte)
            print(soporte)
            extension = os.path.splitext(soporte.archivo.url)[1]
            mime_types = {'.docx': 'application/msword', '.xlsx': 'application/vnd.ms-excel',
                          '.pptx': 'application/vnd.ms-powerpoint',
                          '.xlsm': 'application/vnd.ms-excel.sheet.macroenabled.12',
                          '.dwg': 'application/octet-stream', '.pdf': 'application/pdf',
                          }
            response = HttpResponse(soporte.archivo, content_type=mime_types)
            response['Content-Disposition'] = 'inline; filename="{0} {1} {2}"' \
                .format(actividad.codigo, actividad.nombre, extension)
            return response

        else:
            return render(request, 'GestionActividades/Actividades/index.html')


def datos_xa_render(request, actividad: Actividad = None) -> dict:
    grupos = GrupoActividad.objects.values('id', 'nombre')
    lista_grupos = []
    for grupo in grupos:
        lista_grupos.append({'campo_valor': grupo['id'], 'campo_texto': grupo['nombre']})

    colaboradores = User.objects.values('id', 'first_name', 'last_name')
    lista_colaboradores = []
    for colaborador in colaboradores:
        lista_colaboradores.append({'campo_valor': colaborador['id'],
                                   'campo_texto': colaborador['first_name']+' '+colaborador['last_name']})

    responsable_actividad = ResponsableActividad.objects.get_ids_responsables_list(actividad)
    datos = {'fecha': app_datetime_now(),
             'grupos': lista_grupos,
             'colaboradores': lista_colaboradores,
             'menu_actual': 'actividades',
             'responsable_actividad': responsable_actividad,
             'estado': EstadosActividades.choices}

    if actividad:
        datos['actividad'] = actividad
        datos['editar'] = True

    return datos

