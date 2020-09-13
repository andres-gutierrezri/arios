import datetime
import json

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from EVA import settings
from Notificaciones.models.models import DestinatarioNotificacion, TipoNotificacion, TokenRutaCorreo, \
    SeleccionDeNotificacionARecibir, EventoDesencadenador
from Notificaciones.views.views import construir_notificaciones, crear_notificacion_por_evento


def construir_y_enviar_notificacion_x_email(notificaciones):
    try:
        correos = {}
        for notif in notificaciones:
            if notif['id_not'] not in correos:
                token = get_random_string(length=30)
                TokenRutaCorreo.objects.create(token=token, ruta=notif['ruta'], destinatario_id=notif['id_dest'])
                correos[notif['id_not']] = {'nombre': notif['nombre'], 'mensaje': notif['mensaje'],
                                            'asunto': notif['asunto'], 'token': token,
                                            'lista_destinatarios': [notif['destinatario']]}
            else:
                # Si es más de un destinatario se elimina el nombre, ya que se envia el mismo contenido a todos.
                correos.get(notif['id_not']).pop('nombre')
                correos.get(notif['id_not']).get('lista_destinatarios').append(notif['destinatario'])

        for contenido in correos.values():
            enviar_correo(contenido)

        return True
    except:
        return False


def enviar_correo(contenido):

    plantilla = get_template('Notificaciones/CorreoElectronico/correo.html')
    contenido['eva_acceso_externo'] = settings.EVA_ACCESO_EXTERNO
    contenido['eva_acceso_interno'] = settings.EVA_ACCESO_INTERNO
    email = EmailMessage(
        contenido['asunto'],
        plantilla.render(contenido),
        '"EVA" <noreply@arios-ing.com>',
        [],
        contenido['lista_destinatarios'],
    )
    email.content_subtype = "html"
    email.send()


def enviar_notificacion_por_email(self):

    emails = DestinatarioNotificacion.objects\
        .filter(envio_email_exitoso=False,
                notificacion__fecha_creacion__gt=datetime.date.today() - datetime.timedelta(days=2))

    notificaciones = []
    for email in emails:
        datos = {'id_not': email.notificacion.id, 'id_dest': email.id, 'asunto': email.notificacion.titulo,
                 'nombre': email.usuario.first_name, 'mensaje': email.notificacion.mensaje,
                 'destinatario': email.usuario.email, 'ruta': email.notificacion.evento_desencadenador.ruta}

        if email.notificacion.tipo_notificacion_id == TipoNotificacion.INFORMATIVA:
            if SeleccionDeNotificacionARecibir.objects.filter(evento_desencadenador_id=0, envio_x_email=True,
                                                              usuario=email.usuario):
                notificaciones.append(datos)

        elif email.notificacion.tipo_notificacion_id == TipoNotificacion.EVENTO_DEL_SISTEMA and \
                not email.notificacion.evento_desencadenador_id == EventoDesencadenador.BIENVENIDA:
            seleccion = SeleccionDeNotificacionARecibir.objects \
                        .filter(evento_desencadenador=email.notificacion.evento_desencadenador,
                                usuario=email.usuario)
            if seleccion and seleccion.first().envio_x_email:
                notificaciones.append(datos)
        else:
            notificaciones.append(datos)

    if construir_y_enviar_notificacion_x_email(notificaciones):
        for notif in notificaciones:
            DestinatarioNotificacion.objects.filter(id=notif['id_dest']).update(envio_email_exitoso=True)

    return JsonResponse({"estado": "OK"})


class TokenCorreoView(View):
    def get(self, request, datos):
        destinatario = DestinatarioNotificacion.objects.filter(tokenrutacorreo__token=datos)
        datos = construir_notificaciones(request, limite=None, destinatarios=destinatario)

        if request.user.is_authenticated:
            return render(request, 'EVA/index.html', {'datos': json.dumps(datos)})
        else:
            return render(request, 'Administracion/Autenticacion/iniciar-sesion.html', {'datos': json.dumps(datos)})


def enviar_correo_colaboradores_x_query(request):
    usuarios = User.objects.filter(password="'")
    contador = 0
    for usuario in usuarios:
        if not DestinatarioNotificacion.objects\
                .filter(usuario=usuario, notificacion__evento_desencadenador__id=EventoDesencadenador.BIENVENIDA):
            crear_notificacion_por_evento(EventoDesencadenador.BIENVENIDA, usuario.id, usuario.get_full_name())

            dominio = request.get_host()
            uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            ruta = 'http://{0}/password-reset-confirm/{1}/{2}'.format(dominio, uidb64, token)

            mensaje = "<p>Hola " + usuario.first_name +\
                      ", Te estamos enviando este correo para que asignes una contraseña a tu cuenta en EVA.</p>" \
                      "<p>Tu usuario es: " + usuario.username + "</p>" \
                      "<p>El siguiente enlace te llevará a EVA donde puedes realizar el cambio:</p>" \
                      "<a href=" + ruta + ">Ir a EVA para asignación de la contraseña nueva</a>"

            enviar_correo({'nombre': usuario.first_name,
                           'mensaje': mensaje,
                           'asunto': 'Bienvenido a EVA',
                           'token': False,
                           'lista_destinatarios': [usuario.email]})
            contador += 1
            print("Se le envio el correo a " + usuario.get_full_name())
    print("Fin del proceso")
    if contador > 0:
        print("Se enviaron {0} correos".format(contador))
    else:
        print("No se encontraron usuarios para enviar correos")
    return JsonResponse({"estado": "OK"})
