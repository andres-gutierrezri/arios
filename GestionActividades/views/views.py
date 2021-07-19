from django.shortcuts import render

from EVA.views.index import AbstractEvaLoggedView


class PrincipalView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionActividades/index.html')
