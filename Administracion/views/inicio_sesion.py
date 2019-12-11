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

from TalentoHumano.models import Colaborador


class IniciarSesionView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        else:
            return render(request, 'Administracion/inicio_sesion/iniciar-sesion.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        else:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['colaborador'] = Colaborador.objects.get(usuario=request.user).foto_perfil.url
                messages.success(request, 'Ha iniciado sesión como {0}'.format(username))
                return redirect(reverse('eva-index'))
            else:
                messages.warning(request, 'El usuario y/o la contraseña no son válidos')
                return render(request, 'Administracion/inicio_sesion/iniciar-sesion.html')


class CerrarSesion(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Ha cerrado sesión con éxito')
        return redirect(reverse('eva-index'))


class TerminarSesion(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('Administracion:iniciar-sesion'))


class OlvidoContrasenaView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        else:
            return render(request, 'Administracion/correo/olvido_contrasena.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        else:
            email = request.POST.get('email', '')
            usuario = User.objects.filter(email=email).first()
            if usuario:
                dominio = request.get_host()
                uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
                token = default_token_generator.make_token(usuario)

                plaintext = get_template('Administracion/correo/texto.txt')
                htmly = get_template('Administracion/correo/correo.html')

                d = dict(
                    {'dominio': dominio, 'uidb64': uidb64, 'token': token, 'nombre': usuario.first_name,
                     'usuario': usuario.username})

                subject, from_email, to = 'Bienvenido a Arios Ingenieria SAS', 'noreply@arios-ing.com', \
                                          usuario.email
                text_content = plaintext.render(d)
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                messages.success(request, 'Se ha enviado un mensaje al correo {0}'.format(usuario.email) +
                                 ' con indicaciones para asignar una nueva contraseña')
                return redirect(reverse('Administracion:iniciar-sesion'))
            else:
                messages.warning(request, 'El correo electrónico no es válido')
                return render(request, 'Administracion/correo/olvido_contrasena.html')
