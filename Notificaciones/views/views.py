import datetime

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
