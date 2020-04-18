from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador, SeleccionDeNotificacionARecibir
from TalentoHumano.models import Colaborador


class AsignacionView(AbstractEvaLoggedView):
    def get(self, request, id):
        selecciones = SeleccionDeNotificacionARecibir.objects.filter(usuario_id=id)
        desencadenadores = EventoDesencadenador.objects.exclude(id=EventoDesencadenador.BIENVENIDA)\
            .exclude(permiso=None)
        lista_desencadenador = []
        for desencadenador in desencadenadores:
            if User.objects.get(id=id).has_perms([desencadenador.permiso]):
                lista_desencadenador.append({'id': desencadenador.id,
                                             'nombre': desencadenador.nombre,
                                             'descripcion': desencadenador.descripcion})

        return render(request, 'Notificaciones/AsignacionNotificaciones/asignacion.html',
                      {"desencadenadores": lista_desencadenador,
                       "selecciones": selecciones,
                       "colaborador": {"id": id,
                                       "nombre": Colaborador.objects.get(usuario_id=id).primer_nombre_apellido}})

    def post(self, request, id):
        selecciones = request.POST.getlist("desencadenadores", [])
        SeleccionDeNotificacionARecibir.objects.filter(usuario_id=id).delete()
        for seleccion in selecciones:
            SeleccionDeNotificacionARecibir.objects.create(usuario_id=id, estado=True, envio_x_email=False,
                                                           evento_desencadenador_id=seleccion)
        messages.success(request, 'Se han guardado las selecciones correctamente')
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))
