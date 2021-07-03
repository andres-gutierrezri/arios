import datetime
import json
from sqlite3 import IntegrityError

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Administracion.utils import get_id_empresa_global
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models.models import ConsecutivoReunion
from TalentoHumano.models import Colaborador


class ConsecutivoRequerimientoView(AbstractEvaLoggedView):
    def get(self, request, id):
        return render(request, 'GestionDocumental/ConsecutivoRequerimientos/index.html')


class ConsecutivoRequerimientoCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivoRequerimientos/_modal_crear_editar_consecutivo.html')
