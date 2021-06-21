from django.shortcuts import render

from Administracion.models.models import ReservaSalaJuntas
from EVA.views.index import AbstractEvaLoggedView


class ReservaSalaJuntasView(AbstractEvaLoggedView):
    def get(self, request):
        reserva_sala_juntas = ReservaSalaJuntas.objects.all()
        return render(request, 'Administracion/SalaJuntas/calendario.html',
                      {'reserva_sala_juntas': reserva_sala_juntas, 'menu_actual': 'reserva-sala-juntas'})
