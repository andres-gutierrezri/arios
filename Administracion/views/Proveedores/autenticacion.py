import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db.transaction import atomic
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views import View
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from Administracion.enumeraciones import EstadosProveedor
from Administracion.models import Tercero, TipoIdentificacion, TipoTercero
from EVA import settings
from EVA.General import validar_recaptcha

from EVA.views.index import AbstractEvaLoggedProveedorView
from Notificaciones.models.models import EventoDesencadenador, SeleccionDeNotificacionARecibir
from Notificaciones.views.correo_electronico import enviar_correo
from TalentoHumano.models import Colaborador


class IndexProveedorView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        if request.user.is_authenticated:
            if Tercero.objects.filter(usuario=request.user):
                messages.success(request, 'Ha iniciado sesión como {0}'.format(request.user.first_name))
            else:
                return redirect(reverse('Administracion:iniciar-sesion'))
        return render(request, 'Administracion/index.html')


class InicioSesionProveedorView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if Tercero.objects.filter(usuario=request.user):
                messages.success(request, 'Ha iniciado sesión como {0}'.format(request.user.email))
            else:
                return redirect(reverse('Administracion:iniciar-sesion'))
        return render(request, 'Administracion/Tercero/Proveedor/Autenticacion/inicio-sesion.html',
                      {'recaptcha_site_key': settings.EVA_RECAPTCHA_SITE_KEY})

    def post(self, request):
        if request.user.is_authenticated:
            if Colaborador.objects.filter(usuario=request.user):
                messages.success(request, 'Ha iniciado sesión como {0}'.format(request.user))
                return redirect(reverse('Administracion:proveedor-index'))
        else:
            if validar_recaptcha(request.POST.get('g-recaptcha-response', '')):

                correo = request.POST.get('correo', '')
                password = request.POST.get('password', '')
                usuario = User.objects.filter(username=correo, email=correo)
                user = authenticate(username=correo, password=password)
                if usuario and user is not None:
                    login(request, user)
                    try:
                        request.session['proveedor'] = user.first_name
                        proveedor = Tercero.objects.filter(usuario=user)
                        if proveedor:
                            request.session['proveedor_foto'] = 'EVA/Plantilla/img/profile.png'
                            request.session['proveedor_nombre'] = proveedor.first().nombre
                            request.session['proveedor_correo'] = user.email
                            request.session['proveedor_empresa'] = proveedor.first().empresa_to_dict()
                    except:
                        messages.warning(request, 'El correo y/o la contraseña no son válidos')
                        return redirect(reverse('Administracion:proveedor-iniciar-sesion'))
                else:
                    messages.warning(request, 'El correo y/o la contraseña no son válidos')
                    return redirect(reverse('Administracion:proveedor-iniciar-sesion'))
            else:
                messages.warning(request, 'Captcha inválido')
                return redirect(reverse('Administracion:proveedor-iniciar-sesion'))

        return redirect(reverse('Administracion:proveedor-index'))


class RegistroProveedorView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
        return render(request, 'Administracion/Tercero/Proveedor/registro.html',
                      {'tipo_identificacion': tipo_identificacion,
                       'recaptcha_site_key': settings.EVA_RECAPTCHA_SITE_KEY})

    @atomic
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)

        if validar_recaptcha(datos_registro.get('tokenRecaptcha', '')):
            nombre = datos_registro['nombre']
            correo = datos_registro['correo']
            identificacion = datos_registro['identificacion']
            digito_verificacion = datos_registro['digitoVerificacion'] if datos_registro['digitoVerificacion'] else None

            # usuario = Colaborador.crear_usuario(nombre if len(nombre) < 20 else nombre[:20], 'proveedor', correo)

            tercero = Tercero()
            tercero.nombre = nombre
            tercero.estado = False
            tercero.tipo_tercero_id = TipoTercero.PROVEEDOR
            tercero.tipo_identificacion_id = datos_registro['tipoIdentificacion']
            tercero.identificacion = identificacion
            tercero.digito_verificacion = digito_verificacion
            tercero.tipo_persona = 1 if tercero.tipo_identificacion.sigla == 'NIT' else 2
            tercero.telefono_movil_principal = datos_registro['celular']
            tercero.correo_principal = correo
            tercero.empresa_id = 1
            tercero.nombre_rl = ''
            tercero.identificacion_rl = ''
            tercero.telefono_fijo_principal = ''
            tercero.telefono_fijo_auxiliar = ''
            tercero.telefono_movil_auxiliar = ''
            tercero.correo_auxiliar = ''
            tercero.es_vigente = True
            tercero.estado_proveedor = EstadosProveedor.REGISTRADO

            if User.objects.filter(email=correo):
                return JsonResponse({'estado': 'ERROR', 'mensaje': 'El correo ingresado ya se encuentra registrado'})

            if Tercero.objects.filter(identificacion=identificacion):
                return JsonResponse({'estado': 'ERROR',
                                     'mensaje': 'El número de identificación ingresado ya está registrado'})
            try:
                usuario = User.objects.create(username=correo, first_name=nombre if len(nombre) < 20 else nombre[:20],
                                              last_name=nombre, email=correo)
                tercero.usuario = usuario
                tercero.save()
                SeleccionDeNotificacionARecibir\
                    .objects.create(envio_x_email=True, estado=True, usuario=usuario,
                                    evento_desencadenador_id=EventoDesencadenador.RESPUESTA_SOLICITUD_PROVEEDOR)
                dominio = request.get_host()
                uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
                token = default_token_generator.make_token(usuario)
                ruta = 'http://{0}/password-assign-proveedor/{1}/{2}'.format(dominio, uidb64, token)

                mensaje = "<p>Hola {0}, " \
                          "Te estamos enviando este correo para que asignes una contraseña a tu " \
                          "cuenta de proveedor en EVA.</p>" \
                          "<p>Tu usuario es: {1}</p>" \
                          "<p>El siguiente enlace te llevará a EVA donde puedes realizar la " \
                          "asignación de tu contraseña:</p>" \
                          "<a href={2}>Ir a EVA para asignar una contraseña</a>"\
                    .format(tercero.nombre, usuario.email, ruta)

                enviar_correo({'nombre': tercero.nombre,
                               'mensaje': mensaje,
                               'asunto': 'Bienvenido a EVA',
                               'token': False,
                               'lista_destinatarios': [usuario.email]})
            except:
                return JsonResponse({'estado': 'ERROR'})
        else:
            return JsonResponse({'estado': 'ERROR',
                                 'mensaje': 'Captcha inválido'})

        return JsonResponse({'estado': 'OK', 'datos': {'correo': correo}})
