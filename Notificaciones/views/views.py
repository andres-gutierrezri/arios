import datetime

from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render

from EVA.General import tiempo_transcurrido, app_datetime_now, app_date_now
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import TextoNotificacionDelSistema, Notificacion, TipoNotificacion, \
    SeleccionDeNotificacionARecibir, DestinatarioNotificacion, EventoDesencadenador


def crear_notificacion_por_evento(id_desencadenador, id_evento):

    texto = TextoNotificacionDelSistema.objects.get(evento_desencadenador_id=id_desencadenador)

    notificacion = Notificacion.objects.create(titulo=texto.titulo,
                                               mensaje=texto.mensaje,
                                               id_evento=id_evento,
                                               evento_desencadenador_id=id_desencadenador,
                                               tipo_notificacion_id=TipoNotificacion.EVENTO_DEL_SISTEMA)
    usuario = []
    if id_desencadenador == EventoDesencadenador.BIENVENIDA:
        usuario = [id_evento]

    crear_destinatarios(notificacion, usuario)


def crear_destinatarios(notificacion, lista_usuarios):

    if notificacion.tipo_notificacion_id == TipoNotificacion.EVENTO_DEL_SISTEMA and \
            notificacion.evento_desencadenador_id != EventoDesencadenador.BIENVENIDA:
        selecciones = SeleccionDeNotificacionARecibir.objects \
            .filter(evento_desencadenador=notificacion.evento_desencadenador, estado=True)

        for seleccion in selecciones:
            DestinatarioNotificacion.objects.create(visto=False,
                                                    envio_email_exitoso=False,
                                                    notificacion=notificacion,
                                                    usuario=seleccion.usuario)
    else:
        selecciones = lista_usuarios
        for seleccion in selecciones:
            DestinatarioNotificacion.objects.create(visto=False,
                                                    envio_email_exitoso=False,
                                                    notificacion=notificacion,
                                                    usuario_id=seleccion)


class NotificacionesView(AbstractEvaLoggedView):
    def get(self, request):
        try:
            notificaciones = construir_notificaciones(request, limite=10, destinatarios=[])
            return JsonResponse({"Mensaje": notificaciones['numero_notificaciones'],
                                 "Notificaciones": notificaciones['lista_notificaciones']})
        except IntegrityError:

            return JsonResponse({"Mensaje": "Error interno del servidor", "Notificaciones": []})


class NotificacionesVerTodasView(AbstractEvaLoggedView):
    def get(self, request):
        notificaciones = construir_notificaciones(request, limite=None, destinatarios=[])
        return render(request, 'Notificaciones/ver_todas.html',
                      {"Notificaciones": notificaciones['lista_notificaciones']})


def construir_notificaciones(request, limite, destinatarios):

    if not destinatarios:
        destinatarios = DestinatarioNotificacion.objects \
            .filter(usuario=request.user, notificacion__fecha_creacion__lte=app_datetime_now()) \
            .order_by('-notificacion__fecha_creacion')

    if limite:
        destinatarios = destinatarios[:limite]

    lista_notificaciones = []
    for destinatario in destinatarios:
        fecha = tiempo_transcurrido(destinatario.notificacion.fecha_creacion)

        url = destinatario.notificacion.evento_desencadenador.ruta
        evento = destinatario.notificacion.id_evento

        lista_notificaciones.append(
            {"id": destinatario.notificacion.id,
             "titulo": destinatario.notificacion.titulo,
             "mensaje": destinatario.notificacion.mensaje,
             "fecha": fecha,
             "visto": destinatario.visto,
             "id_evento": evento,
             "modal": destinatario.notificacion.evento_desencadenador.modal,
             "url": url})

    contador_notificaciones = 0
    for dest in destinatarios:
        if not dest.visto and dest.notificacion.fecha_creacion.date() <= app_date_now():
            contador_notificaciones += 1

    return {'lista_notificaciones': lista_notificaciones, 'numero_notificaciones': contador_notificaciones}


class NotificacionesActualizarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            DestinatarioNotificacion.objects.filter(notificacion_id=id, usuario=request.user)\
                .update(visto=True)
            return JsonResponse({"Mensaje": "OK"})

        except IntegrityError:
            return JsonResponse({"Mensaje": "FAIL"})
