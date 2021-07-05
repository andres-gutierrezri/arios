import datetime
import json
from sqlite3 import IntegrityError

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.utils import get_id_empresa_global
from EVA.General.modeljson import RespuestaJson
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models.models import ConsecutivoRequerimiento
from TalentoHumano.models import Colaborador
from TalentoHumano.models.colaboradores import ColaboradorProceso
from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Proyectos.models import Contrato


class ConsecutivoViaticosComisionesView(AbstractEvaLoggedView):
    def get(self, request, id):
        return render(request, 'GestionDocumental/ConsecutivoViaticosComisiones/index.html')
