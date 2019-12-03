from django.shortcuts import render

# Create your views here.
from EVA.views.index import AbstractEvaLoggedView


class Index(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'TalentoHumano/index.html')
