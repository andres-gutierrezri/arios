from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador


class AsignacionView(AbstractEvaLoggedView):
    def get(self, request, id):
        desencadenadores = EventoDesencadenador.objects.all()
        return render(request, 'Notificaciones/AsignacionNotificaciones/asignacion.html',
                      {"desencadenadores": desencadenadores,
                       "colaborador": id})

    def post(self, request, id):
        selecciones = request.POST.getlist("desencadenadores", [])
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))
