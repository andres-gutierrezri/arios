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
from GestionActividades.Enumeraciones import EstadosActividades, EstadosModificacionActividad, TiposUsuariosActividad
from GestionActividades.models.models import Actividad, GrupoActividad, ResponsableActividad, SoporteActividad, \
    AvanceActividad, ModificacionActividad
from Proyectos.models import Contrato
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

        grupos = []
        actividades = []

        if request.user.has_perm('TalentoHumano.permission_gerencial'):
            actividades = Actividad.objects.all().exclude(estado=EstadosActividades.ANULADA)
            grupos = GrupoActividad.objects.get_xa_select_activos().values('id', 'nombre',
                                                                           'grupo_actividad_id', 'estado')

        if request.user.has_perm('TalentoHumano.permission_director_proceso') \
                or request.user.has_perm('TalentoHumano.permission_colaborador_actividad'):
            usuario_id = User.objects.get(username=request.user)
            colaborador_id = Colaborador.objects.get(usuario_id=usuario_id)
            contratos_id = Contrato.objects.get_xa_select_activos().filter(proceso_a_cargo_id=colaborador_id.proceso_id)
            contratos_id = contratos_id.values('id')
            actividades_responsable = ResponsableActividad.objects.filter(responsable_id=colaborador_id.usuario_id)
            actividades_responsable = actividades_responsable.values('actividad_id')

            actividades = Actividad.objects.filter(Q(id__in=actividades_responsable) |
                                                   Q(supervisor_id=colaborador_id.usuario_id)). \
                exclude(estado=EstadosActividades.ANULADA)

            grupos_actividades_ids = actividades.values('grupo_actividad_id')

            grupos = GrupoActividad.objects.get_xa_select_activos().filter(Q(contrato_id__in=contratos_id) |
                                                                           Q(proceso_id=colaborador_id.proceso_id) |
                                                                           Q(id__in=grupos_actividades_ids) |
                                                                           Q(nombre__iexact='Generales'))
            grupos = grupos.values('id', 'nombre', 'grupo_actividad_id', 'estado')

        actividades = actividades.values('id', 'nombre', 'grupo_actividad_id', 'descripcion', 'fecha_fin',
                                         'estado', 'porcentaje_avance', 'soporte_requerido', 'fecha_inicio',
                                         'tiempo_invertido', 'tiempo_estimado', 'supervisor_id')

        responsable_actividad = ResponsableActividad.objects.values('responsable_id', 'actividad_id')
        colaboradores = User.objects.values('id', 'first_name', 'last_name')
        search = request.GET.get('search', '')

        if search:
            actividades = actividades.filter(Q(nombre__icontains=search))

        if id:
            grupos = grupos.filter(Q(id=id) | Q(nombre__iexact='Generales') | Q(grupo_actividad_id=id))

        archivos = SoporteActividad.objects.values('id', 'archivo', 'actividad_id')

        # region Slice para que solo visualizar del archivo el código y el Filename
        archivos_soporte = []
        for archivo in archivos:
            nombre_archivo = archivo['archivo'].split("/")[-1]
            if not nombre_archivo:
                nombre_archivo = '0'

            archivos_soporte.append({'id': archivo['id'], 'archivo': nombre_archivo,
                                     'actividad_id': archivo['actividad_id']})
        # endregion

        avances_actividad = AvanceActividad.objects.values('descripcion', 'fecha_avance', 'tiempo_invertido',
                                                           'porcentaje_avance', 'actividad_id', 'responsable_id')

        usuario_modifica = request.user
        usuario_id = User.objects.get(username=usuario_modifica)

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
                       'usuario_id': usuario_id.id,
                       'menu_actual': 'actividades'})


class ActividadesCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionActividades/Actividades/_crear_editar_actividades_modal.html',
                      datos_xa_render(request))

    def post(self, request):
        try:
            with atomic():
                actividad = Actividad.from_dictionary(request.POST)
                actividad.usuario_crea = request.user
                actividad.usuario_modifica = request.user
                responsables = request.POST.getlist('responsables_id[]', None)
                actividad.fecha_inicio = request.POST.get('fecha_inicio_fin').split(" - ")[0]
                actividad.fecha_fin = request.POST.get('fecha_inicio_fin').split(" - ")[-1]

                if actividad.grupo_actividad_id == '':
                    try:
                        grupo_general = GrupoActividad.objects.get(nombre__iexact='generales')
                        actividad.grupo_actividad_id = grupo_general.id
                    except (GrupoActividad.DoesNotExist, GrupoActividad.MultipleObjectsReturned):
                        return RespuestaJson.error("Falló crear. El grupo Generales no existe")

                try:
                    actividad.full_clean(validate_unique=False, exclude=['motivo'])
                except ValidationError as errores:
                    return RespuestaJson.error("Falló crear. Valide los datos ingresados al crear la actividad")

                if Actividad.objects.filter(nombre__iexact=actividad.nombre,
                                            grupo_actividad_id__exact=actividad.grupo_actividad_id).\
                        exclude(estado=EstadosActividades.ANULADA).exists():
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
                # region Validación si hubo cambios en los responsables de la actividad
                responsables = request.POST.getlist('responsables_id[]', None)

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
                # endregion

                # region Permite determinar si el usuario es supervisor, responsable o ninguno.
                supervisor_actividad = Actividad.objects.get(id=id_actividad)
                responsables_actividad = responsables_actividad_db.values('responsable_id')
                user_modifica = request.user
                user = User.objects.get(username=user_modifica)

                if supervisor_actividad.supervisor_id == user.id:
                    usuario = TiposUsuariosActividad.SUPERVISOR
                else:
                    usuario = TiposUsuariosActividad.NO_ASIGNADO

                for responsable_actividad in responsables_actividad:
                    if responsable_actividad['responsable_id'] == user.id:
                        usuario = TiposUsuariosActividad.RESPONSABLE
                # endregion

                if usuario == TiposUsuariosActividad.SUPERVISOR:
                    update_fields = ['fecha_modificacion', 'codigo', 'supervisor_id', 'fecha_inicio', 'fecha_fin',
                                     'nombre', 'descripcion', 'fecha_creacion', 'motivo', 'usuario_modifica',
                                     'usuario_crea', 'grupo_actividad_id', 'estado', 'soporte_requerido',
                                     'tiempo_estimado']

                    actividad_db = Actividad.objects.get(id=id_actividad)
                    actividad = Actividad.from_dictionary(request.POST)
                    actividad.fecha_inicio = request.POST.get('fecha_inicio_fin').split(" - ")[0]
                    actividad.fecha_fin = request.POST.get('fecha_inicio_fin').split(" - ")[-1]
                    actividad.estado = actividad_db.estado
                    actividad.fecha_creacion = actividad_db.fecha_creacion
                    actividad.id = actividad_db.id
                    actividad.usuario_modifica = request.user
                    actividad.usuario_crea = actividad_db.usuario_crea
                    actividad.tiempo_invertido = actividad_db.tiempo_invertido
                    actividad.soporte_requerido = request.POST.get('soporte_requerido', 'False') == 'True'

                    if actividad.grupo_actividad_id == '':
                        try:
                            grupo_general = GrupoActividad.objects.get(nombre__iexact='generales')
                            actividad.grupo_actividad_id = grupo_general.id
                        except (GrupoActividad.DoesNotExist, GrupoActividad.MultipleObjectsReturned):
                            return RespuestaJson.error("Falló editar. El grupo Generales no existe")

                    try:
                        actividad.full_clean(validate_unique=False)
                    except ValidationError as errores:
                        return RespuestaJson.error("Falló editar. Valide los datos ingresados al editar la actividad")

                    if GrupoActividad.objects.filter(nombre__iexact=actividad.nombre).exists():
                        return RespuestaJson.error(
                            "Falló editar. No puede colocar el mismo nombre de un grupo existente ni"
                            " del grupo que va a contener la actividad")

                    if actividad_db.comparar(actividad, excluir=['fecha_modificacion', 'motivo', 'calificacion',
                                                                 'codigo', 'porcentaje_avance', 'usuario_modifica']) \
                            and conteo_responsables == cantidad_responsables:
                        return RespuestaJson.error("No se hicieron cambios en la actividad")

                    else:
                        actividad.save(update_fields=update_fields)
                        messages.success(request, 'Se ha editado exitosamente la actividad')
                        ResponsableActividad.objects.filter(actividad_id=id_actividad).delete()
                        for responsable in responsables:
                            ResponsableActividad.objects.create(responsable_id=responsable, actividad_id=id_actividad)

                elif usuario == TiposUsuariosActividad.RESPONSABLE:

                    if ModificacionActividad.objects.filter(Q(estado=EstadosModificacionActividad.PENDIENTE)
                                                            & Q(actividad_id=id_actividad)).exists():
                        return RespuestaJson.error("Falló editar.Ya existe una solicitud pendiente por "
                                                   "aprobación para la actividad")

                    actividad_db = Actividad.objects.get(id=id_actividad)
                    modificacion_actividad = ModificacionActividad.from_dictionary(request.POST)
                    modificacion_actividad.fecha_inicio = request.POST.get('fecha_inicio_fin').split(" - ")[0]
                    modificacion_actividad.fecha_fin = request.POST.get('fecha_inicio_fin').split(" - ")[-1]
                    modificacion_actividad.actividad_id = id_actividad
                    modificacion_actividad.nombre = actividad_db.nombre
                    modificacion_actividad.supervisor_id = actividad_db.supervisor_id
                    modificacion_actividad.descripcion = actividad_db.descripcion
                    modificacion_actividad.grupo_actividad_id = actividad_db.grupo_actividad_id
                    modificacion_actividad.soporte_requerido = actividad_db.soporte_requerido
                    modificacion_actividad.usuario_modifica = request.user

                    try:
                        modificacion_actividad.full_clean(validate_unique=False, exclude=['comentario_supervisor'])
                    except ValidationError as errores:
                        return RespuestaJson.error("Falló editar. Valide los datos ingresados al editar la actividad")

                    if actividad_db.fecha_inicio == modificacion_actividad.fecha_inicio \
                            and actividad_db.fecha_fin == modificacion_actividad.fecha_fin \
                            and actividad_db.tiempo_estimado == modificacion_actividad.tiempo_estimado:
                        return RespuestaJson.error("No se hicieron cambios en la actividad")

                    else:
                        modificacion_actividad.save()
                        messages.success(request, 'Se han enviado exitosamente las modificaciones de la '
                                                  'actividad al supervisor')

                else:
                    return RespuestaJson.error("No tiene asignada esta actividad")

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
                update_fields = ['porcentaje_avance', 'tiempo_invertido']
                actividad_db = Actividad.objects.get(id=id_actividad)
                actividad_db.porcentaje_avance = int(avance_actividad.porcentaje_avance)
                tiempo_invertido_avance = float(avance_actividad.tiempo_invertido)
                tiempo_invertido_db = float(actividad_db.tiempo_invertido)
                actividad_db.tiempo_invertido = tiempo_invertido_avance + tiempo_invertido_db
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

        actividades = []

        if request.user.has_perm('TalentoHumano.permission_gerencial'):
            actividades = ModificacionActividad.objects.all()

        if request.user.has_perm('TalentoHumano.permission_director_proceso') or \
                request.user.has_perm('TalentoHumano.permission_colaborador_actividad'):
            usuario_id = User.objects.get(username=request.user)
            colaborador_id = Colaborador.objects.get(usuario_id=usuario_id)
            actividades_responsable = ResponsableActividad.objects.filter(responsable_id=colaborador_id.usuario_id)
            actividades_responsable = actividades_responsable.values('actividad_id')
            actividades_ids = Actividad.objects.filter(Q(id__in=actividades_responsable)).\
                exclude(estado=EstadosActividades.ANULADA)
            actividades_ids = actividades_ids.values('id')
            actividades = ModificacionActividad.objects.filter(Q(supervisor_id=colaborador_id.usuario_id) |
                                                               Q(actividad_id__in=actividades_ids))

        actividades = actividades.values('id', 'nombre', 'motivo', 'estado', 'comentario_supervisor', 'fecha_solicitud',
                                         'fecha_respuesta_solicitud', 'fecha_fin', 'supervisor_id', 'descripcion',
                                         'actividad_id', 'usuario_modifica_id', 'fecha_inicio')

        responsables = User.objects.values('id', 'username', 'first_name', 'last_name')

        usuario = str(request.user)

        return render(request, 'GestionActividades/AprobacionActividades/index.html',
                      {'actividades': actividades,
                       'fecha': app_datetime_now(),
                       'responsables': responsables,
                       'EstadosModificacionActividad': EstadosModificacionActividad,
                       'usuario': usuario,
                       'menu_actual': 'solicitudes-aprobación'})


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
                modificacion_actividad.fecha_respuesta_solicitud = app_datetime_now()
                update_fields = ['estado', 'comentario_supervisor', 'fecha_respuesta_solicitud']
                modificacion_actividad.save(update_fields=update_fields)
                # endregion

                if int(modificacion_actividad.estado) == EstadosModificacionActividad.APROBADA:
                    actividad_db = Actividad.objects.get(id=modificacion_actividad.actividad_id)
                    actividad_db.fecha_inicio = modificacion_actividad.fecha_inicio
                    actividad_db.fecha_fin = modificacion_actividad.fecha_fin
                    actividad_db.tiempo_estimado = modificacion_actividad.tiempo_estimado
                    actividad_db.save()
                    messages.success(request, 'Se han aprobado las modificaciones en la actividad')

                else:
                    messages.success(request, 'Se han rechazado las modificaciones en la actividad')
                return RespuestaJson.exitosa()
        except:
            rollback()
            return RespuestaJson.error("Falló al Editar la actividad")


class VerModificacionesActividadView(AbstractEvaLoggedView):
    def get(self, request, id_actividad):
        modificacion_actividad = ModificacionActividad.objects.get(id=id_actividad)
        actividad = Actividad.objects.get(id=modificacion_actividad.actividad_id)
        return render(request, 'GestionActividades/Actividades/_crear_editar_actividades_modal.html',
                      datos_xa_render(request, actividad, modificacion_actividad))


def datos_xa_render(request, actividad: Actividad = None, modificacion_actividad: ModificacionActividad = None) -> dict:

    grupos = GrupoActividad.objects.get_xa_select_activos()

    lista_colaboradores = Colaborador.objects.get_xa_select_usuarios_activos()

    responsable_actividad = ResponsableActividad.objects.get_ids_responsables_list(actividad)
    datos = {'fecha': app_datetime_now(),
             'grupos': grupos,
             'colaboradores': lista_colaboradores,
             'menu_actual': 'actividades',
             'responsable_actividad': responsable_actividad,
             'estado': EstadosActividades.choices,
             'ocultar_botones_modal': False,
             'actividad_modificada': False}

    if actividad:
        datos['actividad'] = actividad
        datos['editar'] = True

    if modificacion_actividad:
        datos['actividad'] = modificacion_actividad
        datos['modificacion_actividad'] = actividad
        datos['EstadosModificacionActividad'] = EstadosModificacionActividad
        datos['editar'] = True
        datos['ocultar_botones_modal'] = True
        datos['actividad_modificada'] = True

    return datos
