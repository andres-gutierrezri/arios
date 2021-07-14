import logging
import os
import re
from fileinput import filename

from django.contrib.auth.models import User
from django.db.models import Q
from django.db.transaction import rollback, atomic
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render

from django.contrib import messages
from django.core.exceptions import ValidationError

from EVA.General import app_datetime_now, app_date_now
from EVA.General.modeljson import RespuestaJson
from EVA.views.index import AbstractEvaLoggedView
from GestionActividades.Enumeraciones import EstadosActividades
from GestionActividades.models.models import Actividad, GrupoActividad, ResponsableActividad, Soporte

LOGGER = logging.getLogger(__name__)


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

        archivos = Soporte.objects.values('id', 'archivo', 'actividad_id')

        # Slice descartando de la url "privado/GestiónActividades/Actividades/Soportes/" para que solo se
        # visualice del archivo el código y el Filename
        archivos_soporte = []
        for archivo in archivos:
            nombre_archivo = archivo['archivo'][48:]
            if not nombre_archivo:
                nombre_archivo = '0'

            archivos_soporte.append({'id': archivo['id'], 'archivo': nombre_archivo,
                                     'actividad_id': archivo['actividad_id']})
        # endregion

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
        return render(request, 'GestionActividades/Actividades/_crear_editar_actividades_modal.html',
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
        return render(request, 'GestionActividades/Actividades/_crear_editar_actividades_modal.html',
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
        soportes = Soporte.objects.filter(actividad_id=id_actividad)

        if actividad.estado == EstadosActividades.FINALIZADO:
            soporte = soportes.values('fecha_fin', 'descripcion')
            actividad_fecha_finalizacion = soporte[0]['fecha_fin']
            soporte_descripcion = soporte[0]['descripcion']

        else:
            actividad_fecha_finalizacion = ''
            soporte_descripcion = ''

        return render(request, 'GestionActividades/Actividades/_cargar_editar_soportes_modal.html',
                      {'fecha': app_datetime_now(),
                       'actividad': actividad,
                       'actividad_fecha_finalizacion': actividad_fecha_finalizacion,
                       'soporte_descripcion': soporte_descripcion})

    def post(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        try:
            with atomic():
                soporte = Soporte.from_dictionary(request.POST)
                soporte.actividad_id = id_actividad
                # region Guarda los archivos
                for llave in request.FILES:
                    soporte.id = None
                    soporte.archivo = request.FILES.get(llave)
                    soporte.save()
                # endregion
                if not actividad.soporte_requerido:
                    soporte.archivo = None
                    soporte.save()

                # region Actualiza estado actividad
                update_fields = ['estado']
                actividad_db = Actividad.objects.get(id=id_actividad)
                actividad_db.estado = EstadosActividades.FINALIZADO
                actividad_db.save(update_fields=update_fields)
                # endregion

                messages.success(request, 'Se ha finalizado exitosamente la actividad')
                return RespuestaJson.exitosa()
        except:
            rollback()
            # Se contesta con HttpResponseServerError para que el status code sea 500 y lo tome como error el dropzone
            return HttpResponseServerError("Error Finalizando la actividad.")


class VerSoporteView(AbstractEvaLoggedView):
    def get(self, request, id_soporte, id_actividad, archivo):
        actividad = Actividad.objects.get(id=id_actividad)
        if Soporte.objects.filter(id=id_soporte).exists():
            soporte = Soporte.objects.get(id=id_soporte)
            extension = os.path.splitext(soporte.archivo.url)[1]
            mime_types = {'.docx': 'application/msword', '.xlsx': 'application/vnd.ms-excel',
                          '.pptx': 'application/vnd.ms-powerpoint',
                          '.xlsm': 'application/vnd.ms-excel.sheet.macroenabled.12',
                          '.dwg': 'application/octet-stream', '.pdf': 'application/pdf',
                          '.png': 'image/png', '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg'
                          }
            response = HttpResponse(soporte.archivo, content_type=mime_types)
            response['Content-Disposition'] = 'inline; filename="{0}"' \
                .format(archivo)
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
                                    'campo_texto': colaborador['first_name'] + ' ' + colaborador['last_name']})

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
