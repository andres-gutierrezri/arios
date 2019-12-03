# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render, reverse
from django.views import View


class AbstractEvaLoggedView(View):
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super(AbstractEvaLoggedView, self).dispatch(*args, **kwargs)
        else:
            return redirect(reverse('administracion:iniciar-sesion'))


class IndexView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'EVA/index.html')
