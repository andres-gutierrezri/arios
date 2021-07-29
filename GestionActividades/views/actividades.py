import logging
import os
import json

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
from GestionActividades.Enumeraciones import EstadosActividades, EstadosModificacionActividad
from GestionActividades.models.models import Actividad, GrupoActividad, ResponsableActividad, SoporteActividad, \
    AvanceActividad, ModificacionActividad, ResponsableActividadModificacion
from TalentoHumano.models import Colaborador

LOGGER = logging.getLogger(__name__)


class ActividadesIndexView(AbstractEvaLoggedView):
    def get(self, request, id=None):
        actividades = Actividad.objects.values('id', 'estado', 'fecha_inicio')

        for actividad in actividades:
            actividad_db = Actividad.objects.get(id=actividad['id'])
            if actividad['fecha_inicio'] <= app_date_now() and actividad['estado'] == EstadosActividades.CREADA:
                actividad_db.estado = EstadosActividades.EN_PROCESO
                actividad_db.save()
            if actividad['fecha_inicio'] > app_date_now() and actividad['estado'] == EstadosActividades.EN_PROCESO:
                actividad_db.estado = EstadosActividades.CREADA
                actividad_db.save()

        actividades = Actividad.objects.values('id', 'nombre', 'grupo_actividad_id', 'descripcion', 'fecha_fin',
                                               'estado', 'porcentaje_avance', 'soporte_requerido', 'fecha_inicio',
                                               'horas_invertidas', 'tiempo_estimado')
        responsable_actividad = ResponsableActividad.objects.values('responsable_id', 'actividad_id')
        colaboradores = User.objects.values('id', 'first_name', 'last_name')
        grupos = GrupoActividad.objects.values('id', 'nombre', 'grupo_actividad_id', 'estado')
        search = request.GET.get('search', '')

        if search:
            actividades = actividades.filter(Q(nombre__icontains=search))

        if id:
            grupos = grupos.filter(Q(id=id) | Q(nombre__iexact='Generales') | Q(grupo_actividad_id=id))

        archivos = SoporteActividad.objects.values('id', 'archivo', 'actividad_id')

        # Slice descartando de la url "privado/GestiónActividades/Actividades/Soportes/" para que solo se
        # visualice del archivo el código y el Filename
        archivos_soporte = []
        for archivo in archivos:
            nombre_archivo = archivo['archivo'].split("/")[-1]
            if not nombre_archivo:
                nombre_archivo = '0'

            archivos_soporte.append({'id': archivo['id'], 'archivo': nombre_archivo,
                                     'actividad_id': archivo['actividad_id']})
        # endregion

        avances_actividad = AvanceActividad.objects.values('descripcion', 'fecha_avance', 'horas_empleadas',
                                                           'porcentaje_avance', 'actividad_id', 'responsable_id')

        return render(request, 'GestionActividades/Actividades/index.html',
                      {'actividades': actividades,
                       'grupos': grupos,
                       'responsable_actividad': responsable_actividad,
                       'colaboradores': colaboradores,
                       'buscar': search,
                       'archivos_soporte': archivos_soporte,
                       'EstadosActividades': EstadosActividades,
                       'avances_actividad': avances_actividad,
                       'fecha': app_datetime_now(),
                       'menu_actual': 'actividades'})


class ActividadesCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionActividades/Actividades/_crear_editar_actividades_modal.html',
                      datos_xa_render(request))

    def post(self, request):
        try:
            with atomic():
                grupo_actividad = GrupoActividad.from_dictionary(request.POST)
                actividad = Actividad.from_dictionary(request.POST)
                actividad.usuario_crea = request.user
                actividad.usuario_modifica = request.user
                responsables = request.POST.getlist('responsables_id[]', None)

                if actividad.grupo_actividad_id == '':
                    if GrupoActividad.objects.filter(nombre__iexact='generales').exists():
                        grupo_generales = list(GrupoActividad.objects.values('id').filter(nombre__iexact='generales'))
                        actividad.grupo_actividad_id = grupo_generales[0].get('id')
                    else:
                        return RespuestaJson.error("Falló crear. El grupo Generales no existe")

                try:
                    actividad.full_clean(validate_unique=False, exclude=['motivo'])
                except ValidationError as errores:
                    return RespuestaJson.error("Falló crear. Valide los datos ingresados al crear la actividad")

                if Actividad.objects.filter(nombre__iexact=actividad.nombre,
                                            grupo_actividad_id__exact=actividad.grupo_actividad_id).exists():
                    return RespuestaJson.error("Falló crear. Ya existe una actividad con el "
                                               "mismo nombre dentro del grupo")

                elif GrupoActividad.objects.filter(nombre__iexact=actividad.nombre).exists():
                    return RespuestaJson.error("Falló crear. No puede colocar el mismo nombre de un grupo existente ni"
                                               " del grupo que va a contener la actividad")

                else:
                    actividad.save()
                    messages.success(request, 'Se ha creado exitosamente la actividad')
                    for responsable in responsables:
                        ResponsableActividad.objects.create(responsable_id=responsable, actividad=actividad)

                return RespuestaJson.exitosa()
        except:
            rollback()
            return RespuestaJson.error("Falló al crear la actividad")


class ActividadesEditarView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        return render(request, 'GestionActividades/Actividades/_crear_editar_actividades_modal.html',
                      datos_xa_render(request, actividad))

    def post(self, request, id_actividad):
        try:
            with atomic():
                update_fields = ['fecha_modificacion', 'codigo', 'supervisor_id', 'fecha_inicio', 'fecha_fin', 'nombre',
                                 'descripcion', 'fecha_crea', 'motivo', 'usuario_modifica', 'usuario_crea',
                                 'grupo_actividad_id', 'estado', 'soporte_requerido', 'tiempo_estimado']
                grupo_actividad = GrupoActividad.from_dictionary(request.POST)
                actividad = Actividad.from_dictionary(request.POST)
                actividad_db = Actividad.objects.get(id=id_actividad)
                actividad.estado = actividad_db.estado
                actividad.fecha_crea = actividad_db.fecha_crea
                actividad.id = actividad_db.id
                actividad.usuario_modifica = request.user
                actividad.fecha_modificacion = app_datetime_now()
                actividad.usuario_crea = actividad_db.usuario_crea
                actividad.horas_invertidas = actividad_db.horas_invertidas
                responsables = request.POST.getlist('responsables_id[]', None)
                actividad.soporte_requerido = request.POST.get('soporte_requerido', 'False') == 'True'

                if actividad.grupo_actividad_id == '':
                    if GrupoActividad.objects.filter(nombre__iexact='generales').exists():
                        grupo_generales = list(GrupoActividad.objects.values('id').filter(nombre__iexact='generales'))
                        actividad.grupo_actividad_id = grupo_generales[0].get('id')
                    else:
                        return RespuestaJson.error("Falló editar. El grupo Generales no existe")

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
                    return RespuestaJson.error("Falló editar. No puede colocar el mismo nombre de un grupo existente ni"
                                               " del grupo que va a contener la actividad")

                if actividad_db.comparar(actividad, excluir=['fecha_modificacion', 'motivo', 'calificacion', 'codigo',
                                                             'porcentaje_avance', 'usuario_modifica']) \
                        and conteo_responsables == cantidad_responsables:
                    return RespuestaJson.error("No se hicieron cambios en la actividad")

                else:
                    actividad.save(update_fields=update_fields)
                    messages.success(request, 'Se ha editado exitosamente la actividad')
                    ResponsableActividad.objects.filter(actividad_id=id_actividad).delete()
                    for responsable in responsables:
                        ResponsableActividad.objects.create(responsable_id=responsable, actividad_id=id_actividad)

                return RespuestaJson.exitosa()
        except:
            rollback()
            return RespuestaJson.error("Falló al editar la actividad")


class ActualizarActividadView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)

        return render(request, 'GestionActividades/Actividades/_actualizar_actividad_modal.html',
                      {'fecha': app_datetime_now(),
                       'actividad': actividad})

    def post(self, request, id_actividad):
        try:
            with atomic():
                avance_actividad = AvanceActividad.from_dictionary(request.POST)
                avance_actividad.actividad_id = id_actividad
                avance_actividad.responsable = request.user
                avance_actividad.save()

                # region Actualiza el porcentaje y las horas de avance de la actividad
                update_fields = ['porcentaje_avance', 'horas_invertidas']
                actividad_db = Actividad.objects.get(id=id_actividad)
                actividad_db.porcentaje_avance = int(avance_actividad.porcentaje_avance)
                horas_empleadas = float(avance_actividad.horas_empleadas)
                horas_invertidas_db = float(actividad_db.horas_invertidas)
                actividad_db.horas_invertidas = horas_empleadas + horas_invertidas_db
                actividad_db.save(update_fields=update_fields)
                # endregion

                messages.success(request, 'Se ha actualizado exitosamente la actividad')
                return RespuestaJson.exitosa()
        except:
            rollback()
            return RespuestaJson.error("Falló al actualizar la actividad")


class ActividadesEliminarView(AbstractEvaLoggedView):
    def post(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        try:
            with atomic():
                body_unicode = request.body.decode('utf-8')
                datos_registro = json.loads(body_unicode)

                motivo = datos_registro['justificacion']
                if actividad.estado == EstadosActividades.ANULADA:
                    return RespuestaJson.error("Esta actividad ya ha sido eliminada.")
                try:
                    actividad.estado = EstadosActividades.ANULADA
                    actividad.motivo = motivo
                    actividad.save(update_fields=['estado', 'motivo'])
                    messages.success(request, 'Se ha eliminado la actividad {0}'.format(actividad.nombre))
                    return RespuestaJson.exitosa()

                except:
                    return RespuestaJson.error("Ha ocurrido un error al realizar la acción")
        except:
            rollback()
            return RespuestaJson.error("Falló al eliminar la actividad")


class CargarSoporteView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        soportes = SoporteActividad.objects.filter(actividad_id=id_actividad)

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
                soporte = SoporteActividad.from_dictionary(request.POST)
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
    def get(self, request, id_soporte, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        soporte = SoporteActividad.objects.get(id=id_soporte)

        try:
            soporte_url = str(soporte.archivo)
            nombre_archivo = soporte_url.split("/")[-1]
            extension = os.path.splitext(soporte.archivo.url)[1]
            mime_types = {'.docx': 'application/msword', '.xls': 'application/vnd.ms-excel',
                          '.pptx': 'application/vnd.ms-powerpoint', '.DOC': 'application/msword',
                          '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                          '.xlsm': 'application/vnd.ms-excel.sheet.macroenabled.12', '.doc': 'application/msword',
                          '.dwg': 'application/octet-stream', '.pdf': 'application/pdf',
                          '.png': 'image/png', '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg'
                          }
            mime_type = mime_types.get(extension, 'application/pdf')

            response = HttpResponse(soporte.archivo, content_type=mime_type)
            response['Content-Disposition'] = 'inline; filename="{0}"' \
                .format(nombre_archivo)

            return response

        except:
            messages.error(request, 'El archivo soporte no se encuentra disponible')
            return render(request, 'GestionActividades/Actividades/index.html')


class CerrarReabrirActividadView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)

        return render(request, 'GestionActividades/Actividades/_cerrar_reabrir_actividad_modal.html',
                      {'fecha': app_datetime_now(),
                       'EstadosActividades': EstadosActividades,
                       'actividad': actividad})

    def post(self, request, id_actividad):
        try:
            with atomic():
                # region Actualiza el estado y el motivo al Cerrar/Reabrir la actividad
                update_fields = ['calificacion', 'estado', 'motivo', 'usuario_modifica', 'fecha_modificacion']
                actividad_db = Actividad.objects.get(id=id_actividad)
                actividad_db.usuario_modifica = request.user
                actividad_db.motivo = request.POST.get('motivo')
                if actividad_db.estado == EstadosActividades.FINALIZADO or \
                        actividad_db.estado == EstadosActividades.REABIERTA:
                    actividad_db.estado = EstadosActividades.CERRADA
                    actividad_db.calificacion = request.POST.get('calificacion')
                    messages.success(request, 'Se ha Cerrado exitosamente la actividad')
                else:
                    actividad_db.estado = EstadosActividades.REABIERTA
                    messages.success(request, 'Se ha Reabierto exitosamente la actividad')
                actividad_db.save(update_fields=update_fields)
                # endregion

                return RespuestaJson.exitosa()
        except:
            rollback()
            return RespuestaJson.error("Falló al Cerrar/Reabrir la actividad")


class SolicitudesAprobacionActividadIndexView(AbstractEvaLoggedView):
    def get(self, request):
        actividades = ModificacionActividad.objects.values('id', 'nombre', 'motivo', 'estado', 'comentario_supervisor',
                                                           'fecha_solicitud', 'fecha_respuesta_solicitud')

        return render(request, 'GestionActividades/AprobacionActividades/index.html',
                      {'actividades': actividades,
                       'fecha': app_datetime_now(),
                       'EstadosModificacionActividad': EstadosModificacionActividad,
                       'menu_actual': 'solicitudes-aprobación'})


class ModificacionesActividadCrearView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = Actividad.objects.get(id=id_actividad)
        return render(request, 'GestionActividades/AprobacionActividades/_crear_modificaciones_actividad_modal.html',
                      datos_xa_render(request, actividad))

    def post(self, request, id_actividad):
        try:
            with atomic():
                modificacion_actividad = ModificacionActividad.from_dictionary(request.POST)
                modificacion_actividad.actividad_id = id_actividad
                actividad_db = Actividad.objects.get(id=id_actividad)
                responsables = request.POST.getlist('responsables_id[]', None)

                if modificacion_actividad.grupo_actividad_id == '':
                    if GrupoActividad.objects.filter(nombre__iexact='generales').exists():
                        grupo_generales = list(GrupoActividad.objects.values('id').filter(nombre__iexact='generales'))
                        modificacion_actividad.grupo_actividad_id = grupo_generales[0].get('id')
                    else:
                        return RespuestaJson.error("Falló editar. El grupo Generales no existe")

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
                    modificacion_actividad.full_clean(validate_unique=False, exclude=['comentario_supervisor'])
                except ValidationError as errores:
                    return RespuestaJson.error("Falló editar. Valide los datos ingresados al editar la actividad")

                if GrupoActividad.objects.filter(nombre__iexact=modificacion_actividad.nombre).exists():
                    return RespuestaJson.error("Falló editar. No puede colocar el mismo nombre de un grupo existente ni"
                                               " del grupo que va a contener la actividad")

                if actividad_db.comparar(modificacion_actividad, excluir=['fecha_modificacion', 'motivo', 'fecha_crea',
                                                                          'calificacion', 'codigo', 'estado',
                                                                          'usuario_crea', 'actividad_id',
                                                                          'horas_invertidas', 'porcentaje_avance',
                                                                          'usuario_modifica',
                                                                          'comentario_supervisor', 'id']) \
                        and conteo_responsables == cantidad_responsables:
                    return RespuestaJson.error("No se hicieron cambios en la actividad")

                else:
                    modificacion_actividad.save()
                    messages.success(request, 'Se han enviado exitosamente las modificaciones de la '
                                              'actividad al supervisor')
                    for responsable in responsables:
                        ResponsableActividadModificacion.objects.create(responsable_id=responsable,
                                                                        actividad_id=id_actividad)

                return RespuestaJson.exitosa()
        except:
            rollback()
            return RespuestaJson.error("Falló al Editar la actividad")


class AccionModificacionesActividadView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        actividad = ModificacionActividad.objects.get(id=id_actividad)
        opciones_aprobar_rechazar = [{'valor': 2, 'texto': 'Aprobar'},
                                     {'valor': 3, 'texto': 'Rechazar'}]
        return render(request, 'GestionActividades/AprobacionActividades/_accion_modificaciones_actividad_modal.html',
                      {'actividad': actividad,
                       'opciones_aprobar_rechazar': opciones_aprobar_rechazar})

    def post(self, request, id_actividad):
        try:
            with atomic():
                modificacion_actividad = ModificacionActividad.objects.get(id=id_actividad)

                # region Actualiza el estado y el comentario del supervisor al Aprobar/Rechazar cambios de la actividad
                modificacion_actividad.estado = request.POST.get('accion_actividad')
                modificacion_actividad.comentario_supervisor = request.POST.get('comentario_supervisor')
                update_fields = ['estado', 'comentario_supervisor']
                modificacion_actividad.save(update_fields=update_fields)
                # endregion
                print(modificacion_actividad.estado)
                print(EstadosModificacionActividad.APROBADA)
                if int(modificacion_actividad.estado) == EstadosModificacionActividad.APROBADA:
                    messages.success(request, 'Se han aprobado las modificaciones en la actividad')
                else:
                    messages.success(request, 'Se han rechazado las modificaciones en la actividad')
                return RespuestaJson.exitosa()
        except:
            rollback()
            return RespuestaJson.error("Falló al Editar la actividad")


def datos_xa_render(request, actividad: Actividad = None) -> dict:

    grupos = GrupoActividad.objects.get_xa_select_activos()

    usuarios = User.objects.values('id', 'first_name', 'last_name')
    colaboradores = Colaborador.objects.values('usuario_id')
    lista_colaboradores = []
    for usuario in usuarios:
        for colaborador in colaboradores:
            if usuario['id'] == colaborador['usuario_id']:
                lista_colaboradores.append({'campo_valor': usuario['id'],
                                            'campo_texto': usuario['first_name'] + ' ' + usuario['last_name']})

    responsable_actividad = ResponsableActividad.objects.get_ids_responsables_list(actividad)
    datos = {'fecha': app_datetime_now(),
             'grupos': grupos,
             'colaboradores': lista_colaboradores,
             'menu_actual': 'actividades',
             'responsable_actividad': responsable_actividad,
             'estado': EstadosActividades.choices}

    if actividad:
        datos['actividad'] = actividad
        datos['editar'] = True

    return datos
