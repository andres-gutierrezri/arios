from EVA.views.index import AbstractEvaLoggedView
from django.shortcuts import render


class Index(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'Proyectos/index.html')
