from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from Administracion.models.models import ReservaSalaJuntas
from Administracion.views.Proveedores.autenticacion import LOGGER
from EVA.General import app_datetime_now
from EVA.General.conversiones import datetime_to_isostring
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
                                      'color': self.get_color_reserva(reserva.fecha_inicio, reserva.fecha_fin)})

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
                    | Q(fecha_inicio__lte=reserva.fecha_fin, fecha_fin__gte=reserva.fecha_fin)).exists():
            return JsonResponse({"estado": "error", "mensaje": "Ya existe una reunión cargada"})

        # Fecha de inicio este entre el rango de fechas
        # Fecha de fin este entre el rango de fechas
        # Fecha de inicio y la de fin este entre el rango de fechas

        #reserva.save()
        #messages.success(request, 'Se ha creado la reserva en la sala de juntas')
        #return redirect(reverse('Administracion:reserva-sala-juntas'))
        try:
            reserva.save()
        except:
            LOGGER.exception("Error al reunión")
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(request, 'Se ha creado la reserva en la sala de juntas')

        return JsonResponse({"estado": "OK"})


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

        try:
            reserva.full_clean(validate_unique=False)
        except ValidationError as errores:
            messages.error(request, 'Falló editar. Valide los datos ingresados al editar la reserva')
            return redirect(reverse('Administracion:reserva-sala-juntas'))

        if reserva_db.comparar(reserva, excluir=['fecha_modificacion']):
            messages.success(request, 'No se hicieron cambios en la reserva para la sala de juntas')
            return redirect(reverse('Administracion:reserva-sala-juntas'))
        else:
            reserva.save(update_fields=update_fields)
            messages.success(request, 'Se ha editado la reserva para la sala de juntas')
            return redirect(reverse('Administracion:reserva-sala-juntas'))


def datos_xa_render(request, reserva: ReservaSalaJuntas = None) -> dict:
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos_x_empresa(request)

    datos = {'colaboradores': colaboradores,
             'menu_actual': 'reserva-sala-juntas'}

    if reserva:
        datos['reserva'] = reserva
        datos['editar'] = True

    return datos
