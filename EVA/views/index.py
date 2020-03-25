# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.views import View

from EVA.General.validacionpermisos import validar_permisos


class AbstractEvaLoggedView(View):
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
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
