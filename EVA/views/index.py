# -*- coding: utf-8 -*-
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.views import View

from EVA.General.validacionpermisos import validar_permisos
from TalentoHumano.models.colaboradores import ColaboradorEmpresa, Colaborador


class AbstractEvaLoggedView(View):
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if not actualizar_empresa_sesion(self.request):
                return redirect(reverse('administracion:iniciar-sesion'))

            if not validar_permisos(self.request.user, self.request.resolver_match.app_name,
                                    self.request.resolver_match.url_name):

                messages.error(self.request, 'No tiene permisos para acceder a esta funcionalidad')
                return redirect(reverse('eva-index'))

            return super(AbstractEvaLoggedView, self).dispatch(*args, **kwargs)
        else:
            return redirect(reverse('administracion:iniciar-sesion'))


class IndexView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'EVA/index.html')


def actualizar_empresa_sesion(request):
    colaborador = Colaborador.objects.get(usuario=request.user)
    colaborador_empresa = ColaboradorEmpresa.objects.filter(colaborador=colaborador)

    coincidencia = False
    for c_e in colaborador_empresa:
        if c_e.empresa == colaborador.empresa_sesion:
            coincidencia = True

    if not coincidencia:
        colaborador.empresa_sesion = colaborador_empresa.first().empresa
        colaborador.save(update_fields=['empresa_sesion'])
        logout(request)
        return False

    return True
