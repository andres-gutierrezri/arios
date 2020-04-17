from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import SeleccionDeNotificacionARecibir

OPCION = 'correo'


class SeleccionNotificacionEmailView(AbstractEvaLoggedView):
    def get(self, request, id):
        selecciones = SeleccionDeNotificacionARecibir.objects.filter(usuario_id=id)\
            .order_by('evento_desencadenador__nombre')
        lista_desencadenador = []
        for seleccion in selecciones:
            lista_desencadenador.append({'id': seleccion.evento_desencadenador.id,
                                         'nombre': seleccion.evento_desencadenador.nombre,
                                         'descripcion': seleccion.evento_desencadenador.descripcion,
                                         'correo': seleccion.envio_x_email})

        return render(request, 'Notificaciones/AsignacionNotificaciones/asignacion.html',
                      {"selecciones": selecciones,
                       "desencadenadores": lista_desencadenador,
                       "colaborador": id,
                       "opcion": OPCION})

    def post(self, request, id):
        selecciones = request.POST.getlist("desencadenadores", [])
        SeleccionDeNotificacionARecibir.objects.filter(usuario_id=id).update(envio_x_email=False)
        for seleccion in selecciones:
            SeleccionDeNotificacionARecibir.objects.filter(evento_desencadenador_id=seleccion, usuario_id=id)\
                .update(envio_x_email=True)
        messages.success(request, 'Se han guardado las selecciones correctamente')
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))
