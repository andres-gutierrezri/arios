from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, reverse
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
