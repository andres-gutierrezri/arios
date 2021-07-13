import json
import random

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from sqlite3 import IntegrityError
from django.db.models import Q
from Administracion.models.models import ReservaSalaJuntas
from Administracion.parametros import ParametrosAdministracion
from Administracion.views.Proveedores.autenticacion import LOGGER
from EVA.General import app_datetime_now
from EVA.General.conversiones import datetime_to_isostring
from EVA.General.modeljson import RespuestaJson
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from TalentoHumano.models import Colaborador

# Constante para convertir minutos a segundos y viceversa
SEGUNDOS: int = 60

# Colores para la reserva
COLORES = ['#BDB4AB', '#BB9676', '#CFB606', '#B9B937', '#6BC41D', '#55A60E', '#5CB480', '#85AB8A', '#1EBE81', '#81B4A1',
           '#28BEC0', '#039395', '#05AACB', '#4DC3DA', '#4D98DA', '#0079E3', '#2473B8', '#3033BF', '#6669FF', '#C76BFF',
           '#CE00F7', '#D982EA', '#FF61C3', '#FF818F', '#E2EC3E', '#00E1DB', '#AEABEA', '#948EFF', '#F700FF', '#00A6FF']

# Parámetro de holgura
params_sala_juntas = ParametrosAdministracion.get_params_sala_juntas()
param_holgura = params_sala_juntas.get_holgura()


class ReservaSalaJuntasView(AbstractEvaLoggedView):
    def get(self, request):
        fecha_actual = app_datetime_now()

        reuniones = ReservaSalaJuntas.objects.filter(fecha_inicio__date=fecha_actual.date()) \
            .filter(fecha_fin__lt=fecha_actual).filter(finalizacion=False, notificacion=False) \
            .exclude(estado=False)

        for reunion in reuniones:
            crear_notificacion_por_evento(EventoDesencadenador.CIERRE_RESERVA_SALA_JUNTAS, reunion.id,
                                          contenido={'titulo': f'Pendiente finalización de la Reserva de la '
                                                               f'Sala de Juntas',
                                                     'mensaje': f'Se recuerda que al terminar la reunión en la sala de '
                                                                f'juntas se debe finalizar la reserva con el tema: '
                                                                f'{reunion.tema}',
                                                     'usuario': reunion.responsable_id})
            reunion.notificacion = True
            reunion.save(update_fields=['notificacion'])

        if request.resolver_match.url_name == 'reserva-sala-juntas-json':
            reservas = ReservaSalaJuntas.objects.filter(Q(fecha_inicio__date__gte=fecha_actual.date())
                                                        | Q(fecha_fin__date=fecha_actual.date()))
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
        fecha_actual = app_datetime_now()

        if reserva.fecha_inicio <= fecha_actual <= reserva.fecha_fin:
            return 'red'  # color = HEX#FF0000
        elif reserva.fecha_fin < fecha_actual:
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

        past_dates = ReservaSalaJuntas.objects.filter(fecha_fin__date=reserva.fecha_inicio.date()) \
            .filter(fecha_fin__lt=reserva.fecha_inicio).exclude(estado=False).values_list('fecha_fin', flat=True)

        for date in range(len(past_dates)):
            holgura = (reserva.fecha_inicio - past_dates[date]).seconds
            if holgura < param_holgura * SEGUNDOS:
                reserva_actual = reserva.fecha_inicio.astimezone()
                reserva_anterior = past_dates[date].astimezone()
                reserva_holgura = (reserva_actual - reserva_anterior).seconds // SEGUNDOS
                if reserva_holgura == 1:
                    tiempo = "minuto"
                else:
                    tiempo = "minutos"
                return RespuestaJson.error(f'Debe haber un espacio mínimo de {param_holgura} minutos '
                                           f'entre el inicio de la de reunión ({reserva_actual.strftime("%H:%M")}) '
                                           f'y el final de la anterior ({reserva_anterior.strftime("%H:%M")}). '
                                           f'Hay una diferencia de: {reserva_holgura} {tiempo}')

        later_dates = ReservaSalaJuntas.objects.filter(fecha_inicio__date=reserva.fecha_fin.date()) \
            .filter(fecha_inicio__gt=reserva.fecha_fin).exclude(estado=False).values_list('fecha_inicio', flat=True)

        for date in range(len(later_dates)):
            holgura = (later_dates[date] - reserva.fecha_fin).seconds
            if holgura < param_holgura * SEGUNDOS:
                reserva_actual = reserva.fecha_fin.astimezone()
                reserva_posterior = later_dates[date].astimezone()
                reserva_holgura = (reserva_posterior - reserva_actual).seconds // SEGUNDOS
                if reserva_holgura == 1:
                    tiempo = "minuto"
                else:
                    tiempo = "minutos"
                return RespuestaJson.error(f'Debe haber un espacio mínimo de {param_holgura} minutos '
                                           f'entre el final de la de reunión ({reserva_actual.strftime("%H:%M")}) '
                                           f'y el inicio de la siguiente ({reserva_posterior.strftime("%H:%M")}). '
                                           f'Hay una diferencia de: {reserva_holgura} {tiempo}')
        try:
            reserva.save()
        except:
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

        past_dates = ReservaSalaJuntas.objects.filter(fecha_fin__date=reserva.fecha_inicio.date()) \
            .filter(fecha_fin__lt=reserva.fecha_inicio).exclude(estado=False) \
            .exclude(id=id_reserva).values_list('fecha_fin', flat=True)

        for date in range(len(past_dates)):
            holgura = (reserva.fecha_inicio - past_dates[date]).seconds
            if holgura < param_holgura * SEGUNDOS:
                reserva_actual = reserva.fecha_inicio.astimezone()
                reserva_anterior = past_dates[date].astimezone()
                reserva_holgura = (reserva_actual - reserva_anterior).seconds // SEGUNDOS
                if reserva_holgura == 1:
                    tiempo = "minuto"
                else:
                    tiempo = "minutos"
                return RespuestaJson.error(f'Debe haber un espacio mínimo de {param_holgura} minutos '
                                           f'entre el inicio de la de reunión ({reserva_actual.strftime("%H:%M")}) '
                                           f'y el final de la anterior ({reserva_anterior.strftime("%H:%M")}). '
                                           f'Hay una diferencia de: {reserva_holgura} {tiempo}')

        later_dates = ReservaSalaJuntas.objects.filter(fecha_inicio__date=reserva.fecha_fin.date()) \
            .filter(fecha_inicio__gt=reserva.fecha_fin).exclude(estado=False) \
            .exclude(id=id_reserva).values_list('fecha_inicio', flat=True)

        for date in range(len(later_dates)):
            holgura = (later_dates[date] - reserva.fecha_fin).seconds
            if holgura < param_holgura * SEGUNDOS:
                reserva_actual = reserva.fecha_fin.astimezone()
                reserva_posterior = later_dates[date].astimezone()
                reserva_holgura = (reserva_posterior - reserva_actual).seconds // SEGUNDOS
                if reserva_holgura == 1:
                    tiempo = "minuto"
                else:
                    tiempo = "minutos"
                return RespuestaJson.error(f'Debe haber un espacio mínimo de {param_holgura} minutos '
                                           f'entre el final de la de reunión ({reserva_actual.strftime("%H:%M")}) '
                                           f'y el inicio de la siguiente ({reserva_posterior.strftime("%H:%M")}). '
                                           f'Hay una diferencia de: {reserva_holgura} {tiempo}')

        if reserva_db.comparar(reserva, excluir=['fecha_modificacion', 'usuario_modifica', 'motivo']):
            return RespuestaJson.exitosa(mensaje="No se hicieron cambios en la reserva para la sala de juntas")
        else:
            reserva.save(update_fields=update_fields)
            return RespuestaJson.exitosa(mensaje="Se ha editado la reserva para la sala de juntas")


class ReservaSalaJuntasEliminarView(AbstractEvaLoggedView):
    def post(self, request, id_reserva):
        reserva_db = ReservaSalaJuntas.objects.get(id=id_reserva)
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)
        motivo = datos_registro['justificacion']

        if not reserva_db.estado:
            return RespuestaJson.error("La reserva ya ha sido eliminada")
        try:
            reserva_db.usuario_modifica = request.user
            reserva_db.estado = False
            reserva_db.motivo = motivo
            reserva_db.save(update_fields=['estado', 'motivo', 'usuario_modifica', 'fecha_modificacion'])
            return RespuestaJson.exitosa()

        except IntegrityError:
            return RespuestaJson.error("No se puede eliminar la reserva {0}".format(reserva_db.tema))


class ReservaSalaJuntasFinalizarView(AbstractEvaLoggedView):
    def post(self, request, id_reserva):
        reserva_db = ReservaSalaJuntas.objects.get(id=id_reserva)

        if reserva_db.finalizacion:
            return RespuestaJson.error("La reserva ya ha sido finalizada")
        try:
            fecha_actual = app_datetime_now()
            if reserva_db.fecha_fin >= fecha_actual:
                reserva_db.fecha_fin = fecha_actual
            reserva_db.usuario_modifica = request.user
            reserva_db.finalizacion = True
            reserva_db.save(update_fields=['fecha_fin','finalizacion', 'usuario_modifica', 'fecha_modificacion'])
            return RespuestaJson.exitosa(mensaje="La reserva ha sido finalizada")

        except IntegrityError:
            return RespuestaJson.error("No se puede finalizar la reserva {0}".format(reserva_db.tema))


def datos_xa_render(request, reserva: ReservaSalaJuntas = None) -> dict:
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos_x_empresa(request)
    fecha_actual = app_datetime_now()

    datos = {'colaboradores': colaboradores,
             'menu_actual': 'reserva-sala-juntas'}

    if reserva:
        datos['reserva'] = reserva
        datos['editar'] = True
        datos['cierre'] = reserva.fecha_fin < fecha_actual and not reserva.finalizacion
        datos['finalizar'] = reserva.fecha_inicio <= fecha_actual <= reserva.fecha_fin

    return datos
