from EVA.General.validacionpermisos import tiene_permisos
from EVA.views.index import AbstractEvaLoggedView
from django.shortcuts import render, redirect, reverse

# Create your views here.


class Index(AbstractEvaLoggedView):
    def get(self, request):
        if not tiene_permisos(request, 'Proyectos', None, None):
            return redirect(reverse('eva-index'))
        else:
            return render(request, 'Proyectos/index.html')
