from django.shortcuts import render

# Create your views here.
from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView


class Index(AbstractEvaLoggedView):
    def get(self, request):
        procesos = Proceso.objects.all()
        return render(request, 'SGI/index.html', {'procesos': procesos})
