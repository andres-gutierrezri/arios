from django.shortcuts import render
from EVA.views.index import AbstractEvaLoggedView


class Index(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'TalentoHumano/index.html')
