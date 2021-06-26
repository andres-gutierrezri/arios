from datetime import datetime

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models.models import ReservaSalaJuntas
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

        reserva.save()
        messages.success(request, 'Se ha creado la reserva en la sala de juntas')
        return redirect(reverse('Administracion:reserva-sala-juntas'))


def datos_xa_render(request) -> dict:
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos_x_empresa(request)

    datos = {'colaboradores': colaboradores,
             'menu_actual': 'reserva-sala-juntas'}

    return datos
