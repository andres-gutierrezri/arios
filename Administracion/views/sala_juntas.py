import json
from datetime import datetime

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from sqlite3 import IntegrityError
from django.db.models import Q
from Administracion.models.models import ReservaSalaJuntas
from Administracion.views.Proveedores.autenticacion import LOGGER
from EVA.General import app_datetime_now
from EVA.General.conversiones import datetime_to_isostring, datetime_to_utc
from EVA.General.modeljson import RespuestaJson
from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models import Colaborador


class ReservaSalaJuntasView(AbstractEvaLoggedView):
    def get(self, request):
        if request.resolver_match.url_name == 'reserva-sala-juntas-json':
            reservas = ReservaSalaJuntas.objects.all()
            reservas_dict = []

            for reserva in reservas:
                reservas_dict.append({'id': reserva.id, 'title': f'{reserva.tema} \n {reserva.responsable.username}',
                                      'start': datetime_to_isostring(reserva.fecha_inicio),
                                      'end': datetime_to_isostring(reserva.fecha_fin),
                                      'color': self.get_color_reserva(reserva.fecha_inicio, reserva.fecha_fin),
                                      'className': 'mostrar' if reserva.estado else 'ocultar'})

            return JsonResponse(reservas_dict, safe=False)
        else:
            return render(request, 'Administracion/SalaJuntas/calendario.html',
                          {'menu_actual': 'reserva-sala-juntas'})

    @staticmethod
    def get_color_reserva(fecha_inicio: datetime, fecha_fin: datetime):
        actual = app_datetime_now()
        if fecha_fin < actual:
            return 'gray'
        elif fecha_inicio > actual:
            return 'blue'
        else:
            return 'green'


class ReservaSalaJuntasCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'Administracion/SalaJuntas/modal_crear_editar_reserva.html', datos_xa_render(request))

    def post(self, request):
        reserva = ReservaSalaJuntas.from_dictionary(request.POST)
        reserva.usuario_crea = request.user
        reserva.fecha_creacion = app_datetime_now()

        if ReservaSalaJuntas.objects \
                .filter(Q(fecha_inicio__lte=reserva.fecha_inicio, fecha_fin__gte=reserva.fecha_inicio)
                        | Q(fecha_inicio__lte=reserva.fecha_fin, fecha_fin__gte=reserva.fecha_fin)) \
                .exclude(estado=False).exists():
            return RespuestaJson.error("Ya existe una reunión asignada en este horario")

        try:
            reserva.save()
        except:
            LOGGER.exception("Error en la reserva")
            return RespuestaJson.error("Ha ocurrido un error al guardar la información")

        return RespuestaJson.exitosa(mensaje="Se ha creado la reserva en la sala de juntas")


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
        reserva.usuario_modifica = request.user

        if ReservaSalaJuntas.objects \
            .filter(Q(fecha_inicio__lte=reserva.fecha_inicio, fecha_fin__gte=reserva.fecha_inicio)
                    | Q(fecha_inicio__lte=reserva.fecha_fin, fecha_fin__gte=reserva.fecha_fin))\
                .exclude(estado=False).exclude(id=id_reserva).exists():
            return RespuestaJson.error("Ya existe una reunión asignada en este horario")

        try:
            reserva.full_clean(validate_unique=False)
        except ValidationError as errores:
            return RespuestaJson.error("Falló la edición. Valide los datos ingresados al editar la reserva")

        reserva.fecha_inicio = datetime_to_utc(reserva.fecha_inicio)
        reserva.fecha_fin = datetime_to_utc(reserva.fecha_fin)

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
            return RespuestaJson.error("La reserva ha sido eliminada")
        try:
            reserva_db.usuario_modifica = request.user
            reserva_db.estado = False
            reserva_db.motivo = motivo
            reserva_db.save(update_fields=['estado', 'motivo', 'usuario_modifica', 'fecha_modificacion'])
            return RespuestaJson.exitosa()

        except IntegrityError:
            return RespuestaJson.error("No se puede eliminar la reserva {0}".format(reserva_db.tema))


def datos_xa_render(request, reserva: ReservaSalaJuntas = None) -> dict:
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos_x_empresa(request)

    datos = {'colaboradores': colaboradores,
             'menu_actual': 'reserva-sala-juntas'}

    if reserva:
        datos['reserva'] = reserva
        datos['editar'] = True

    return datos
