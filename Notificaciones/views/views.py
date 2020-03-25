import datetime

from django.db import IntegrityError
from django.http import JsonResponse

from EVA.General.conversiones import distancia_entre_fechas_a_texto
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import TextoNotificacionDelSistema, Notificacion, TipoNotificacion, \
    SeleccionDeNotificacionARecibir, DestinatarioNotificacion, EventoDesencadenador


def crear_notificacion_por_evento(id_desencadenador, id_evento):

    texto = TextoNotificacionDelSistema.objects.get(evento_desencadenador_id=id_desencadenador)

    notificacion = Notificacion.objects.create(titulo=texto.titulo,
                                               mensaje=texto.mensaje,
                                               fecha_creacion=datetime.datetime.today(),
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
            contador = 0
            limite_notificaciones = 10
            destinatarios = DestinatarioNotificacion.objects.filter(usuario=request.user)\
                .order_by('-notificacion__fecha_creacion')
            lista_notificaciones = []
            for destinatario in destinatarios:
                if destinatario.notificacion.fecha_creacion.date() <= datetime.date.today():
                    fecha = distancia_entre_fechas_a_texto(destinatario.notificacion.fecha_creacion)
                    contador += 1

                    if destinatario.notificacion.tipo_notificacion_id == TipoNotificacion.EVENTO_DEL_SISTEMA:
                        url = destinatario.notificacion.evento_desencadenador.ruta
                        evento = destinatario.notificacion.id_evento
                    else:
                        url = '/notificaciones/detalle-info-oblig'
                        evento = destinatario.notificacion.id

                    lista_notificaciones.append(
                        {"id": destinatario.notificacion.id,
                         "titulo": destinatario.notificacion.titulo,
                         "mensaje": destinatario.notificacion.mensaje,
                         "fecha": fecha,
                         "visto": destinatario.visto,
                         "id_evento": evento,
                         "url": url})
                    if contador > limite_notificaciones:
                        break
            contador_notificaciones = 0
            for dest in destinatarios:
                if not dest.visto and dest.notificacion.fecha_creacion.date() <= datetime.date.today():
                    contador_notificaciones += 1
            return JsonResponse({"Mensaje": contador_notificaciones,
                                 "Notificaciones": lista_notificaciones})

        except IntegrityError:

            return JsonResponse({"Mensaje": "Error interno del servidor", "Notificaciones": []})