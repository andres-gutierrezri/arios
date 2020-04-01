import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import CadenaAprobacionEncabezado
from SGI.models.documentos import CadenaAprobacionDetalle, Archivo
from TalentoHumano.models import Colaborador


class CadenaAprobacionView(AbstractEvaLoggedView):
    def get(self, request):
        cadenas_aprobacion = CadenaAprobacionEncabezado.objects.all()
        fecha = datetime.now()
        return render(request, 'SGI/CadenasAprobacion/index.html', {'cadenas_aprobacion': cadenas_aprobacion,
                                                                    'fecha': fecha,
                                                                    'menu_actual': 'cadenas_aprobacion'})
