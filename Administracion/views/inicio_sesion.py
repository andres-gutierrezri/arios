from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, reverse
from django.views import View


class IniciarSesionView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-indexindex'))
        else:
            return render(request, 'Administracion/inicio_sesion/iniciar-sesion.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('index'))
        else:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                return redirect(reverse('eva-index'))
            else:
                error = 'Usuario y/o contraseña no validos'
                return render(request, 'Administracion/inicio_sesion/iniciar-sesion.html', {'error': error})


class CerrarSesion(View):
    def get(self, request):
        logout(request)
        request.session['empresa'] = ''
        return redirect(reverse('inventario:iniciar-sesion'))
