import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.views import View

from Notificaciones.models.models import DestinatarioNotificacion, TipoNotificacion, TokenRutaCorreo, \
    SeleccionDeNotificacionARecibir, EventoDesencadenador
from Notificaciones.views.views import construir_notificaciones


def enviar_mensaje_x_email(notificaciones):
    try:
        lista_notificaciones = []
        for notif in notificaciones:
            existe = False
            for lista in lista_notificaciones:
                if lista == notif['id_not']:
                    existe = True
            if not existe:
                lista_notificaciones.append(notif['id_not'])

        for id_not in lista_notificaciones:
            lista_destinatarios = []
            asunto = ''
            nombre = ''
            mensaje = ''
            ruta = ''
            id_dest = ''
            for notif in notificaciones:
                if id_not == notif['id_not']:
                    asunto = notif['asunto']
                    nombre = notif['nombre']
                    mensaje = notif['mensaje']
                    ruta = notif['ruta']
                    id_dest = notif['id_dest']
                    lista_destinatarios.append(notif['destinatario'])
            token = get_random_string(length=30)
            TokenRutaCorreo.objects.create(token=token, ruta=ruta, destinatario_id=id_dest)
            plantilla = get_template('Notificaciones/CorreoElectronico/correo.html')
            contenido = dict({'nombre': nombre, 'mensaje': mensaje, 'asunto': asunto, 'token': token})

            email = EmailMessage(
                asunto,
                plantilla.render(contenido),
                'noreply@arios-ing.com',
                [],
                lista_destinatarios,
                headers={'Message-ID': 'foo'},
            )
            email.content_subtype = "html"
            email.send()
            EmailMessage()

        return True

    except:
        return False


def enviar_notificacion_por_email(self):

    fecha = datetime.date.today() - datetime.timedelta(days=2)

    emails = DestinatarioNotificacion.objects.filter(envio_email_exitoso=False,
                                                     notificacion__fecha_creacion__gt=fecha)

    notificaciones = []
    for email in emails:
        datos = {'id_not': email.notificacion.id,
                 'id_dest': email.id,
                 'asunto': email.notificacion.titulo,
                 'nombre': email.usuario.first_name,
                 'mensaje': email.notificacion.mensaje,
                 'destinatario': email.usuario.email,
                 'ruta': email.notificacion.evento_desencadenador.ruta}

        if email.notificacion.tipo_notificacion_id == TipoNotificacion.OBLIGATORIA:
            notificaciones.append(datos)

        elif email.notificacion.tipo_notificacion_id == TipoNotificacion.INFORMATIVA:
            correo = SeleccionDeNotificacionARecibir.objects \
                     .filter(evento_desencadenador_id=0, usuario=email.usuario, envio_x_email=True)
            if correo:
                notificaciones.append(datos)
        elif email.notificacion.tipo_notificacion_id == TipoNotificacion.EVENTO_DEL_SISTEMA and \
                email.notificacion.evento_desencadenador_id == EventoDesencadenador.BIENVENIDA:
            notificaciones.append(datos)

        elif email.notificacion.tipo_notificacion_id == TipoNotificacion.EVENTO_DEL_SISTEMA:
            seleccion = SeleccionDeNotificacionARecibir.objects \
                        .filter(evento_desencadenador=email.notificacion.evento_desencadenador,
                                usuario=email.usuario)
            if seleccion:
                if seleccion.first().envio_x_email:
                    notificaciones.append(datos)

    if enviar_mensaje_x_email(notificaciones):
        for notif in notificaciones:
            DestinatarioNotificacion.objects.filter(id=notif['id_dest']).update(envio_email_exitoso=True)

    return JsonResponse({"Mensaje": "OK"})


class TokenCorreoView(View):
    def get(self, request, datos):
        destinatario = DestinatarioNotificacion.objects.filter(tokenrutacorreo__token=datos)
        datos = construir_notificaciones(request, limite=None, destinatarios=destinatario)

        if request.user.is_authenticated:
            return render(request, 'EVA/index.html', {'datos': json.dumps(datos)})
        else:
            return render(request, 'Administracion/Autenticacion/iniciar-sesion.html', {'datos': json.dumps(datos)})
