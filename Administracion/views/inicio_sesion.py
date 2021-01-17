from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render, reverse
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.contrib import messages

from Administracion.models import Tercero
from Notificaciones.views.correo_electronico import enviar_correo
from TalentoHumano.models import Colaborador


class IniciarSesionView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        else:
            return render(request, 'Administracion/Autenticacion/iniciar-sesion.html')

    def post(self, request):
        if request.user.is_authenticated:
            proveedor = Tercero.objects.filter(usuario=request.user)
            if proveedor:
                return redirect(reverse('Administracion:proveedor-index'))
            else:
                return redirect(reverse('eva-index'))
        else:
            datos = request.POST.get('datos')
            username: str = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username.lower(), password=password)
            proveedor = User.objects.filter(username=username, email=username)
            if user is not None and not proveedor:
                login(request, user)
                try:
                    colaborador = Colaborador.objects.get(usuario=request.user)
                    request.session['colaborador'] = colaborador.foto_perfil.url
                    request.session['colaborador_id'] = colaborador.id
                    request.session['empresa'] = colaborador.empresa_to_dict()
                    messages.success(request, 'Ha iniciado sesión como {0}'.format(username))
                except Colaborador.DoesNotExist:
                    if user.is_superuser:
                        request.session['colaborador_id'] = 0
                        messages.warning(request, f'Ha iniciado sesión como {username} pero no tiene un perfil')
                    else:
                        messages.error(request, f'Usuario sin perfil')
                        logout(request)
                        return render(request, 'Administracion/Autenticacion/iniciar-sesion.html')

                if datos:
                    return render(request, 'EVA/index.html', {'datos': datos})
                else:
                    return redirect(reverse('eva-index'))
            else:
                messages.warning(request, 'El usuario y/o la contraseña no son válidos')
                return render(request, 'Administracion/Autenticacion/iniciar-sesion.html')


class CerrarSesion(View):
    def get(self, request):
        autenticado = request.user.is_authenticated
        proveedor = False

        if autenticado:
            if Tercero.objects.filter(usuario=request.user):
                proveedor = True

        logout(request)
        if autenticado:
            messages.success(request, 'Ha cerrado sesión con éxito')
        if proveedor:
            return redirect(reverse('Administracion:proveedor-iniciar-sesion'))
        else:
            return redirect(reverse('Administracion:iniciar-sesion'))


class OlvidoContrasenaView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        else:
            return render(request, 'Administracion/Autenticacion/olvido_contrasena.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        else:
            email = request.POST.get('email', '')
            usuario = User.objects.filter(email=email).first()
            proveedor = Tercero.objects.filter(usuario=usuario, es_vigente=True)
            if usuario and not proveedor:
                dominio = request.get_host()
                uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
                token = default_token_generator.make_token(usuario)

                ruta = 'http://{0}/password-reset-confirm/{1}/{2}'.format(dominio, uidb64, token)

                mensaje = "<p>Hola " + usuario.first_name + ", " \
                          "<p>Se ha generado una solicitud de recuperación de contraseña"\
                          "<p>Tu usuario es: " + usuario.username + "</p>" \
                          "<p>El siguiente enlace te redireccionará a la página donde puedes realizar el cambio:</p>" \
                          "<a href=" + ruta + ">Ir a la página para reestablecer la contraseña</a>"

                enviar_correo({'nombre': usuario.first_name,
                               'mensaje': mensaje,
                               'asunto': 'Reestablecimiento de Contraseña',
                               'token': False,
                               'lista_destinatarios': [usuario.email]})

                messages.success(request, 'Se ha enviado un mensaje al correo {0}'.format(usuario.email) +
                                 ' con indicaciones para asignar una nueva contraseña')

                return redirect(reverse('Administracion:iniciar-sesion'))
            else:
                messages.warning(request, 'El correo electrónico no es válido')
                return render(request, 'Administracion/Autenticacion/olvido_contrasena.html')


class OlvidoContrasenaProveedorView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('administracion:proveedor-index'))
        else:
            return render(request, 'Administracion/Tercero/Proveedor/Autenticacion/olvido_contrasena.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('administracion:proveedor-index'))
        else:
            email = request.POST.get('email', '')
            usuario = User.objects.filter(email=email).first()
            proveedor = Tercero.objects.filter(usuario=usuario, es_vigente=True)
            if proveedor:
                dominio = request.get_host()
                uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
                token = default_token_generator.make_token(usuario)
                proveedor = Tercero.objects.filter(usuario=usuario)

                ruta = 'http://{0}/password-reset-confirm-proveedor/{1}/{2}'.format(dominio, uidb64, token)

                mensaje = "<p>Hola " + proveedor.first().nombre + ", " \
                          "<p>Se ha generado una solicitud de recuperación de contraseña"\
                          "<p>Tu usuario es: " + usuario.email + "</p>" \
                          "<p>El siguiente enlace te redireccionará a la página donde puedes realizar el cambio:</p>" \
                          "<a href=" + ruta + ">Ir a la página para reestablecer la contraseña</a>"

                enviar_correo({'nombre': proveedor.first().nombre,
                               'mensaje': mensaje,
                               'asunto': 'Reestablecimiento de Contraseña',
                               'token': False,
                               'lista_destinatarios': [usuario.email]})

                messages.success(request, 'Se ha enviado un mensaje al correo {0}'.format(usuario.email) +
                                 ' con indicaciones para asignar una nueva contraseña')

                return redirect(reverse('Administracion:proveedor-iniciar-sesion'))
            else:
                messages.warning(request, 'El correo electrónico no es válido')
                return render(request, 'Administracion/Tercero/Proveedor/Autenticacion/olvido_contrasena.html')
