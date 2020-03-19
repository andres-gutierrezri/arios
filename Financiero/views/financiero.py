from django.shortcuts import render, reverse, redirect
from EVA.General.validacionpermisos import tiene_permisos
from EVA.views.index import AbstractEvaLoggedView


class PrincipalView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'Financiero/index.html')
