import json
import random
import datetime

from django.core.exceptions import ValidationError
from django.db.transaction import atomic, rollback
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from Administracion.models.sala_juntas import ReservaSalaJuntas
from Administracion.parametros import ParametrosAdministracion
from Administracion.views.Proveedores.autenticacion import LOGGER
from EVA.General import app_datetime_now
from EVA.General.conversiones import datetime_to_isostring, SEGUNDOS_EN_MIN
from EVA.General.modeljson import RespuestaJson
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from TalentoHumano.models import Colaborador


# Colores para la reserva
COLORES = ['#BDB4AB', '#BB9676', '#CFB606', '#B9B937', '#6BC41D', '#55A60E', '#5CB480', '#85AB8A', '#1EBE81', '#81B4A1',
           '#28BEC0', '#039395', '#05AACB', '#4DC3DA', '#4D98DA', '#0079E3', '#2473B8', '#3033BF', '#6669FF', '#C76BFF',
           '#CE00F7', '#D982EA', '#FF61C3', '#FF818F', '#E2EC3E', '#00E1DB', '#AEABEA', '#948EFF', '#F700FF', '#00A6FF']


class ReservaSalaJuntasView(AbstractEvaLoggedView):
    def get(self, request):
        if request.resolver_match.url_name == 'reserva-sala-juntas-json':

            reservas = ReservaSalaJuntas.objects.filter(Q(fecha_inicio__date__gte=datetime.date.today())
                                                        | Q(fecha_fin__date=datetime.date.today()))
            reservas_dict = []
            for reserva in reservas:
                reservas_dict.append({'id': reserva.id, 'title': f'{reserva.tema} \n {reserva.responsable.username}',
                                      'start': datetime_to_isostring(reserva.fecha_inicio),
                                      'end': datetime_to_isostring(reserva.fecha_fin),
                                      'color': self.get_color_reserva(reserva),
                                      'className': 'mostrar' if reserva.estado else 'ocultar'})

            return JsonResponse(reservas_dict, safe=False)
        else:
            return render(request, 'Administracion/SalaJuntas/calendario.html',
                          {'menu_actual': 'reserva-sala-juntas'})

    @staticmethod
    def get_color_reserva(reserva: ReservaSalaJuntas) -> str:
        if reserva.fecha_inicio <= app_datetime_now() <= reserva.fecha_fin:
            return 'red'  # color = HEX#FF0000
        elif reserva.fecha_fin < app_datetime_now():
            if reserva.finalizacion:
                return 'gray'  # color = HEX#808080
            else:
                return 'orange'  # color = HEX#FF8000
        else:
            return reserva.color


class ReservaSalaJuntasCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'Administracion/SalaJuntas/modal_crear_editar_reserva.html', datos_xa_render(request))

    def post(self, request):
        reserva = ReservaSalaJuntas.from_dictionary(request.POST)
        reserva.usuario_crea = request.user
        reserva.fecha_creacion = app_datetime_now()
        reserva.color = self.get_color_reserva(COLORES)

        if ReservaSalaJuntas.objects \
                .filter(Q(fecha_inicio__lte=reserva.fecha_inicio, fecha_fin__gte=reserva.fecha_inicio)
                        | Q(fecha_inicio__lte=reserva.fecha_fin, fecha_fin__gte=reserva.fecha_fin)
                        | Q(fecha_inicio__gt=reserva.fecha_inicio, fecha_fin__lt=reserva.fecha_fin)) \
                .exclude(estado=False).exists():
            return RespuestaJson.error("Ya existe una reunión asignada en este horario")

        resval = reserva.validar_holgura()
        if resval:
            return RespuestaJson.error(resval)

        try:
            with atomic():
                reserva.save()
        except:
            rollback()
            LOGGER.exception("Error en la reserva")
            return RespuestaJson.error("Ha ocurrido un error al guardar la información")

        return RespuestaJson.exitosa(mensaje="Se ha creado la reserva en la sala de juntas")

    @staticmethod
    def get_color_reserva(colores) -> str:
        color = random.choice(colores)
        return color


class ReservaSalaJuntasEditarView(AbstractEvaLoggedView):
    def get(self, request, id_reserva):
        reserva = ReservaSalaJuntas.objects.get(id=id_reserva)

        return render(request, 'Administracion/SalaJuntas/modal_crear_editar_reserva.html',
                      datos_xa_render(request, reserva))

    def post(self, request, id_reserva):
        update_fields = ['responsable', 'tema', 'fecha_inicio', 'fecha_fin', 'descripcion', 'motivo',
                         'fecha_modificacion', 'usuario_modifica']

        reserva = ReservaSalaJuntas.from_dictionary(request.POST)
        reserva_db = ReservaSalaJuntas.objects.get(id=id_reserva)

        reserva.id = reserva_db.id
        reserva.fecha_creacion = reserva_db.fecha_creacion
        reserva.usuario_crea = reserva_db.usuario_crea
        reserva.color = reserva_db.color
        reserva.usuario_modifica = request.user

        if ReservaSalaJuntas.objects \
                .filter(Q(fecha_inicio__lte=reserva.fecha_inicio, fecha_fin__gte=reserva.fecha_inicio)
                        | Q(fecha_inicio__lte=reserva.fecha_fin, fecha_fin__gte=reserva.fecha_fin)
                        | Q(fecha_inicio__gt=reserva.fecha_inicio, fecha_fin__lt=reserva.fecha_fin)) \
                .exclude(estado=False).exclude(id=id_reserva).exists():
            return RespuestaJson.error("Ya existe una reunión asignada en este horario")

        try:
            reserva.full_clean(validate_unique=False)
        except ValidationError as errores:
            return RespuestaJson.error("Falló la edición. Valide los datos ingresados al editar la reserva")

        resval = reserva.validar_holgura(True)
        if resval:
            return RespuestaJson.error(resval)

        if reserva_db.comparar(reserva, excluir=['fecha_modificacion', 'usuario_modifica', 'motivo']):
            return RespuestaJson.exitosa(mensaje="No se hicieron cambios en la reserva para la sala de juntas")

        try:
            with atomic():
                reserva.save(update_fields=update_fields)
                return RespuestaJson.exitosa(mensaje="Se ha editado la reserva para la sala de juntas")
        except:
            rollback()
            LOGGER.exception("Error editando una reserva de sala de juntas.")
            return RespuestaJson.error("Se presentó un error al editar la reserva de sala de juntas.")


class ReservaSalaJuntasEliminarView(AbstractEvaLoggedView):
    def post(self, request, id_reserva):
        reserva_db = ReservaSalaJuntas.objects.get(id=id_reserva)
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)
        motivo = datos_registro['justificacion']

        if not reserva_db.estado:
            return RespuestaJson.error("La reserva ya ha sido eliminada")
        try:
            with atomic():
                reserva_db.usuario_modifica = request.user
                reserva_db.estado = False
                reserva_db.motivo = motivo
                reserva_db.save(update_fields=['estado', 'motivo', 'usuario_modifica', 'fecha_modificacion'])
                return RespuestaJson.exitosa()
        except:
            rollback()
            LOGGER.exception("Error al eliminar una reserva de sala de juntas.")
            return RespuestaJson.error("No se puede eliminar la reserva {0}".format(reserva_db.tema))


class ReservaSalaJuntasFinalizarView(AbstractEvaLoggedView):
    def post(self, request, id_reserva):
        reserva_db = ReservaSalaJuntas.objects.get(id=id_reserva)

        if reserva_db.finalizacion:
            return RespuestaJson.error("La reserva ya ha sido finalizada")
        try:
            with atomic():
                if reserva_db.fecha_fin >= app_datetime_now():
                    reserva_db.fecha_fin = app_datetime_now()
                reserva_db.usuario_modifica = request.user
                reserva_db.finalizacion = True
                reserva_db.save(update_fields=['fecha_fin', 'finalizacion', 'usuario_modifica', 'fecha_modificacion'])
                return RespuestaJson.exitosa(mensaje="La reserva ha sido finalizada")
        except:
            rollback()
            LOGGER.exception("Error finalizando una reserva de sala de juntas.")
            return RespuestaJson.error("No se puede finalizar la reserva {0}".format(reserva_db.tema))


class ReservaSalaJuntasNotificacionView(AbstractEvaLoggedView):
    def get(self, request):
        notificaciones_generadas: bool = False

        reservas = ReservaSalaJuntas.objects.filter(fecha_inicio__date=datetime.date.today()) \
            .filter(fecha_fin__lt=app_datetime_now()).filter(finalizacion=False, notificacion=False) \
            .exclude(estado=False)

        # Parámetro de holgura
        param_holgura = ParametrosAdministracion.get_params_sala_juntas().get_holgura()

        for reserva in reservas:
            if (app_datetime_now() - reserva.fecha_fin).seconds >= param_holgura * SEGUNDOS_EN_MIN:
                crear_notificacion_por_evento(EventoDesencadenador.CIERRE_RESERVA_SALA_JUNTAS, reserva.id,
                                              contenido={'titulo': 'Pendiente Finalizar Reserva Sala de Juntas',
                                                         'mensaje': f'Al terminar la reunión se debe finalizar '
                                                                    f'la reserva ({reserva.tema})',
                                                         'usuario': reserva.responsable_id})

                reserva.notificacion = notificaciones_generadas = True
                reserva.save(update_fields=['notificacion'])

        if notificaciones_generadas:
            return JsonResponse({"estado": "OK", "mensaje": "Notificaciones generadas"})
        else:
            return JsonResponse({"estado": "OK", "mensaje": "En espera para generar las notificaciones"})


def datos_xa_render(request, reserva: ReservaSalaJuntas = None) -> dict:
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos_x_empresa(request)

    datos = {'colaboradores': colaboradores,
             'menu_actual': 'reserva-sala-juntas'}

    if reserva:
        datos['reserva'] = reserva
        datos['editar'] = True
        datos['cierre'] = reserva.fecha_fin < app_datetime_now() and not reserva.finalizacion
        datos['finalizar'] = reserva.fecha_inicio <= app_datetime_now() <= reserva.fecha_fin

    return datos
