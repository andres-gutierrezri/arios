from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

from Administracion.models.models import ReservaSalaJuntas
from EVA.General import app_datetime_now
from EVA.General.conversiones import datetime_to_isostring
from EVA.views.index import AbstractEvaLoggedView


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
